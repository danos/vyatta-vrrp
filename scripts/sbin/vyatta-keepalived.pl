#!/usr/bin/perl
#
# Module: vyatta-keepalived.pl
#
# **** License ****
#
# Copyright (c) 2018,2019 AT&T Intellectual Property. All rights reserved.
# Copyright (c) 2014 by Brocade Communications Systems, Inc.
# All rights reserved.
#
# This code was originally developed by Vyatta, Inc.
# Portions created by Vyatta are Copyright (C) 2007-2009 Vyatta, Inc.
# All Rights Reserved.
#
# Author: Stig Thormodsrud
# Date: October 2007
# Description: Script to glue vyatta cli to keepalived daemon
#
# SPDX-License-Identifier: GPL-2.0-only
#
# **** End License ****
#

use lib "/opt/vyatta/share/perl5/";
use Vyatta::Config;
use Vyatta::Keepalived;
use Vyatta::Interface;
use Vyatta::Misc;
use Vyatta::VRRP::virtual_interface;
use Getopt::Long;
use Net::IP;

use strict;
use warnings;

my ( $action, $vrrp_intf, $vrrp_group, $vrrp_vip, $connsync );
my ( $conf_file, $changes_file, $intf_file );
my %HoA_sync_groups;
my %tracked_ifs;
my %tracked_monitors;
my %tracked_routes;
my $sync_dp_script = "/opt/vyatta/sbin/vyatta-vrrp-csyncd.sh";
my %virtual_interfaces;

sub keepalived_get_values {
  my ( $intf, $path , $noerr) = @_;

  my @loc;
  my $err;
  my @errs   = ();
  my $output = '';
  my $intf_mapping = '';
  my $config = new Vyatta::Config;

  my $state_transition_script = get_state_script();
  my $run_default_script = "/opt/vyatta/sbin/vyatta-log-vrrp-transition.pl";
  my $ipsec_transition_script;
  my $bgp_transition_script;
  my $notify_flag = 0;

  my $notify_dbus_client_script = "/opt/vyatta/sbin/dbus-notify";
  my $notify_dbus_client_sub_args = "";
  my $notify_dbus_client_args = "";

  my $on_off = "off";
  $on_off = "on" if $noerr;
  vrrp_log("keepalived_get_values [$intf][$path] noerr = $on_off");
  $config->setLevel($path);
  my @intf_addr = $config->returnValues("address");
  if ( $config->isDeleted("vrrp") ) {
      return ($output, @errs) if $noerr;
      vrrp_log("vrrp_instance [$intf] deleted");
      return ( $output, @errs );      
  }

  $config->setLevel("$path vrrp");
  my $start_delay = $config->returnValue("start-delay");
  $config->setLevel("$path vrrp vrrp-group");
  my @groups = $config->listNodes();
  foreach my $group (@groups) {
    # Reset the tracked interfaces and monitor hashes per group
    %tracked_ifs = ();
    %tracked_monitors = ();
    %tracked_routes = ();
    my $vrrp_instance = "vyatta-$intf-$group";
    $config->setLevel("$path vrrp vrrp-group $group");
    if ( $config->exists("disable") ) {
      next if $noerr;
      vrrp_log("$vrrp_instance disabled - skipping");
      my $state_file = get_state_file( $intf, $group );
      unlink($state_file);
      next;
    }
    my @vips     = $config->returnValues("virtual-address");

    # Only need to look at first vip since Yang model guarantees that the
    # vip list will only contain addresses from one address family.
    my $af = Vyatta::Misc::is_ip_v4_or_v6($vips[0]);

    # Extra vIP list checking required for IPv6 address-family
    if ( $af == 6 ) {
        # This group's vIP list needs to be re-ordered so that link-local
        # addresses are at the start of the list. This is because the
        # primary (first) address in a VRRPv3 IPv6 group must be link-local
        # to satisfy RFC5798.
        #
        # Re-ordering is carried out by pulling all the link-local addresses
        # into a seperate list and appending them to the start of the 
        # vIP list. If the the link-local address list is empty, then
        # there is no primary link-local to use with this VRRPv3 IPv6 group
        # therefore commit of this configuration must FAIL.
        
        # Pull the link-local addresses out. In IPv6 link-local addresses
        # start with FE80.
        my @ll_addrs = grep(/^fe80/i, @vips);

        # Pull the non link-local addresses out. In IPv6 link-local addresses
        # start with FE80.
        my @leftover_addrs = grep(!/^fe80/i, @vips);

        # Wipe the @vip list, this will be recreated in the correct order.
        @vips = ();

        # Add the link-local list to the vIP list.
        push(@vips, @ll_addrs);

        # Add the non link-local addresses to the vIP list.
        push(@vips, @leftover_addrs);
    }

    my $use_vmac = 0;
    my $transition_intf = $intf;
    my $prefix = $intf;
    $prefix =~ s/(\w\w\d+)(.*)/$1/;

    if ( $config->exists("rfc-compatibility") ) {
        $use_vmac        = 1;
        if (!%virtual_interfaces) {
            $transition_intf = $prefix."vrrp1";
            $virtual_interfaces{$vrrp_instance} = $transition_intf;
        } elsif (exists $virtual_interfaces{$vrrp_instance}) {
            $transition_intf = $virtual_interfaces{$vrrp_instance};
        } else {
            my $largest_virt_int = get_largest_virtual_interface(%virtual_interfaces);
            $transition_intf = increment_virtual_interface($largest_virt_int);
            $transition_intf =~ s/(\w\w\d+)(.*)/$prefix$2/;
            $virtual_interfaces{$vrrp_instance} = $transition_intf;
            if ( (length $transition_intf) > 15 ) {
                print "Warning: generated interface name is longer than 15 characters\n";
                $use_vmac = 0;
            }
        }
    }

    my $version = $config->returnValue("version");

    my $priority = $config->returnValue("priority");
    if ( !defined $priority ) {
        $priority = 100;    # Default backup priority is 100 from RFC.
    }

    my $preempt = $config->returnValue("preempt");

    my $accept = $config->returnValue("accept");

    my $preempt_delay = $config->returnValue("preempt-delay");
    if ( defined $preempt_delay and $preempt eq "false" ) {
      print "Warning: preempt delay is ignored when preempt=false\n";
    }
    my $advert_int = $config->returnValue("advertise-interval");
    my $fast_advert_int = $config->returnValue("fast-advertise-interval");

    if ( !defined $advert_int && !defined $fast_advert_int ) {
        $advert_int = 1;
    }
    if ( defined $fast_advert_int && $version == 3 ) {
        $advert_int = $fast_advert_int / 1000;
    }
    my $sync_group = $config->returnValue("sync-group");
    if ( defined $sync_group && $sync_group ne "" ) {
      push @{ $HoA_sync_groups{$sync_group} }, $vrrp_instance;
    }
    my $hello_source_addr = $config->returnValue("hello-source-address");

    $config->setLevel("$path vrrp vrrp-group $group");
    my ($auth_type, $auth_pass) = (undef, undef);
    if ($config->exists('authentication')) {
      $config->setLevel("$path vrrp vrrp-group $group authentication");
      $auth_type = $config->returnValue("type");
      $auth_pass = $config->returnValue("password");
      $auth_type = "PASS" if $auth_type eq "plaintext-password";
      $auth_type = uc($auth_type);
    } 
    $config->setLevel("$path vrrp vrrp-group $group");
    if ( $config->exists("notify ipsec") ) {
      $ipsec_transition_script = "/opt/vyatta/sbin/vyatta-ipsec-notify.sh";
      $notify_flag = 1;
    }
    if ( $config->exists("notify bgp") ) {
      $bgp_transition_script = "/opt/vyatta/sbin/notify-bgp";
      $notify_flag = 1;
    }

    $config->setLevel("$path vrrp vrrp-group $group run-transition-scripts");
    my $run_transition_scripts = 0;
    my $run_backup_script = $config->returnValue("backup");
    if ( !defined $run_backup_script ) {
      $run_backup_script = "null";
    } else {
      $run_transition_scripts++;
    }
    my $run_fault_script = $config->returnValue("fault");
    if ( !defined $run_fault_script ) {
      $run_fault_script = "null";
    } else {
      $run_transition_scripts++;
    }
    my $run_master_script = $config->returnValue("master");
    if ( !defined $run_master_script ) {
      $run_master_script = "null";
    } else {
      $run_transition_scripts++;
    }
    $config->setLevel("$path vrrp vrrp-group $group");
    my $track_iface = $config->exists("track-interface");
    if ( defined $track_iface ) {
        my @tifs = $config->listNodes("track-interface");
        foreach my $tif (@tifs) {
            $tracked_ifs{$tif} = undef;
            if ( $config->exists("track-interface $tif weight") ) {
                my $val  =
                  $config->returnValue("track-interface $tif weight value");
                my $type =
                  $config->returnValue("track-interface $tif weight type");
                $tracked_ifs{$tif} =
                  $type eq "increment" ? "+$val" : "-$val";
            }
        }
    }

    # Look for enhanced tracking config.
    $config->setLevel("$path vrrp vrrp-group $group");
    my $track_level = $config->exists("track");
    my $en_track_iface;
    my $en_track_monitor;
    my $en_track_route;
    if ( defined $track_level) {
        $config->setLevel("$path vrrp vrrp-group $group track");

        # Find interface tracking config
        $en_track_iface = $config->exists("interface");
        if ( defined $en_track_iface ) {
            my @tifs = $config->listNodes("interface");
            foreach my $tif (@tifs) {
                $tracked_ifs{$tif} = undef;
                if ( $config->exists("interface $tif weight") ) {
                    my $val  =
                      $config->returnValue("interface $tif weight value");
                    my $type =
                      $config->returnValue("interface $tif weight type");
                    $tracked_ifs{$tif} =
                      $type eq "increment" ? "+$val" : "-$val";
                }
            }
        }

        # Find path monitor tracking config
        $en_track_monitor = $config->exists("path-monitor");
        if ( defined $en_track_monitor ) {
            my @tpms = $config->listNodes("path-monitor monitor");
            foreach my $tpm (@tpms) {
                $tracked_monitors{$tpm} = undef;
                my @tpps = $config->listNodes("path-monitor monitor $tpm policy");
                foreach my $tpp (@tpps) {
                    $tracked_monitors{$tpm}{$tpp} = undef;
                    if ( $config->exists("path-monitor monitor $tpm policy $tpp weight") ) {
                        my $val  =
                          $config->returnValue("path-monitor monitor $tpm policy $tpp weight value");
                        my $type =
                          $config->returnValue("path-monitor monitor $tpm policy $tpp weight type");
                        $tracked_monitors{$tpm}{$tpp}{"weight"} =
                          $type eq "increment" ? "+$val" : "-$val";
                    }
                }
            }
        }

        # Find route-to tracking config
        $en_track_route = $config->exists("route-to");
        if ( defined $en_track_route ) {
            my @troutes = $config->listNodes("route-to");
            foreach my $troute (@troutes) {
                $tracked_routes{$troute} = undef;
                if ( $config->exists("route-to $troute weight") ) {
                    my $val  =
                      $config->returnValue("route-to $troute weight value");
                    my $type =
                      $config->returnValue("route-to $troute weight type");
                    $tracked_routes{$troute} =
                      $type eq "increment" ? "+$val" : "-$val";
                }
            }
        }
    }

    # We now have the values and have validated them, so
    # generate the config.

    $output .= "vrrp_instance $vrrp_instance \{\n";
    my $init_state;
    $init_state = vrrp_get_init_state( $intf, $group, $vips[0], $preempt );
    $output .= "\tstate $init_state\n";
    $output .= "\tinterface $intf\n";
    $output .= "\tvirtual_router_id $group\n";
    my ($ip, $len) = Net::IP::ip_splitprefix($vips[0]);
    if ( Net::IP::ip_is_ipv6($ip) ) {
        $output .= "\tnative_ipv6\n";
    }
    #
    # Put the version number before the use_vmac string.
    # The vmac we use depends on whether or not we're running V2 or V3.
    # For V3 IPv6 we have to use a different vmac from V2
    #
    if ( defined $version ) {
        $output .= "\tversion $version\n";
    }
    if ($use_vmac) {
	$output .= "\tuse_vmac $transition_intf\n";
	$intf_mapping .= "$transition_intf=" . $intf . "v" . $group . "\n";
        $output .= "\tvmac_xmit_base\n";
    }
    $output .= "\tpriority $priority\n";
    if ( $preempt eq "false" ) {
      $output .= "\tnopreempt\n";
    }
    if ( $accept eq "true" ) {
        $output .= "\taccept\n";
    }
    if ( defined $start_delay ) {
      $output .= "\tstart_delay $start_delay\n";
    }
    if ( defined $preempt_delay ) {
      $output .= "\tpreempt_delay $preempt_delay\n";
    }
    $output .= "\tadvert_int $advert_int\n";
    if ( defined $auth_type ) {
      $output .= "\tauthentication {\n";
      $output .= "\t\tauth_type $auth_type\n";
      $output .= "\t\tauth_pass $auth_pass\n\t}\n";
    }
    if ( defined $hello_source_addr ) {
      $output .= "\tmcast_src_ip $hello_source_addr\n";
    }
    $output .= "\tvirtual_ipaddress \{\n";
    foreach my $vip (@vips) {
      $output .= "\t\t$vip\n";
    }
    $output .= "\t\}\n";
    if (defined $track_iface || defined $en_track_iface || defined $en_track_monitor || defined $en_track_route) {
        $output .= "\ttrack \{\n";
        if ( defined $track_iface || defined $en_track_iface ) {
            $output .= "\t\tinterface \{\n";
            foreach my $tif ( keys %tracked_ifs ) {
                $output .= "\t\t\t$tif";
                if ( defined $tracked_ifs{$tif} ) {
                    $output .= "\tweight\t";
                    $output .= $tracked_ifs{$tif};
                }
                $output .= "\n";
            }
            $output .= "\t\t\}\n";
        }

        if ( defined $en_track_monitor ) {
            $output .= "\t\tpathmon \{\n";
            my $monitor_output = "";
            foreach my $tpm ( keys %tracked_monitors ) {
                $monitor_output = "\t\t\tmonitor $tpm";
                foreach my $tpp ( keys %{$tracked_monitors{$tpm}} ) {
                    $output .= "$monitor_output\tpolicy $tpp";
                    if ( defined $tracked_monitors{$tpm}{$tpp}{"weight"} ) {
                        $output .= "\tweight\t";
                        $output .= $tracked_monitors{$tpm}{$tpp}{"weight"};
                    }
                    $output .= "\n";
                }
            }
            $output .= "\t\t\}\n";
        }

        if ( defined $en_track_route ) {
            $output .= "\t\troute_to \{\n";
            foreach my $troute ( keys %tracked_routes ) {
                $output .= "\t\t\t$troute";
                if ( defined $tracked_routes{$troute} ) {
                    $output .= "\tweight\t";
                    $output .= $tracked_routes{$troute};
                }
                $output .= "\n";
            }
            $output .= "\t\t\}\n";
        }
        $output .= "\t\}\n";
    }
    # When transition scripts are ran they modify a file to set the new state of
    # the VRRP group. If only one state change has a script configured this
    # generated file can contain a stale state. The logic below adds default
    # scripts to states that do not have a configured script, if at least one
    # state has an explicitly configured script.
    if ($run_master_script ne 'null') {
      $output .= "\tnotify_master \"$state_transition_script master ";
      $output .= "$intf $group $transition_intf \'$run_master_script\' @vips\" \n";
    } elsif ($run_master_script eq 'null' && $run_transition_scripts > 0) {
      $output .= "\tnotify_master \"/opt/vyatta/sbin/vyatta-vrrp-state.pl master ";
      $output .= "$intf $group $transition_intf \'$run_default_script\' @vips\" \n";
    }
    if ($run_backup_script ne 'null') {
      $output .= "\tnotify_backup \"$state_transition_script backup ";
      $output .= "$intf $group $transition_intf \'$run_backup_script\' @vips\" \n";
    } elsif ($run_backup_script eq 'null' && $run_transition_scripts > 0) {
      $output .= "\tnotify_backup \"/opt/vyatta/sbin/vyatta-vrrp-state.pl backup ";
      $output .= "$intf $group $transition_intf \'$run_default_script\' @vips\" \n";
    }
    if ($run_fault_script ne 'null') {
      $output .= "\tnotify_fault \"$state_transition_script fault ";
      $output .= "$intf $group $transition_intf \'$run_fault_script\' @vips\" \n";
    } elsif ($run_fault_script eq 'null' && $run_transition_scripts > 0) {
      $output .= "\tnotify_fault \"/opt/vyatta/sbin/vyatta-vrrp-state.pl fault ";
      $output .= "$intf $group $transition_intf \'$run_default_script\' @vips\" \n";
    }
    if ($notify_flag == 1) {
      $notify_dbus_client_sub_args = "$intf,$group";
      $output .= "\tnotify \{\n";
        if (defined $ipsec_transition_script) {
          $output .= "\t\t$ipsec_transition_script\n";
		  $notify_dbus_client_sub_args .= ",$ipsec_transition_script";
        }
        if (defined $bgp_transition_script) {
          $output .= "\t\t$bgp_transition_script\n";
		  $notify_dbus_client_sub_args .= ",$bgp_transition_script";
        } 
      $output .= "\t\}\n";
    }
    $output .= "\}\n\n";
    # Reset so subsequent groups under the same interface will only
    # have notify config if its actually configured.
    $bgp_transition_script = undef;
    $ipsec_transition_script = undef;
    $notify_flag = 0;

	$notify_dbus_client_args .= " $notify_dbus_client_sub_args";
    $notify_dbus_client_sub_args = "";
  }

  # start notify daemon
  system($notify_dbus_client_script $notify_dbus_client_args);

  return ( $output, $intf_mapping, @errs );
}

sub vrrp_is_connsync_cfg {
  my $cfg = new Vyatta::Config;
  if ($cfg->exists("service connsync")) {
     return 1;
  }
  return;
}

sub vrrp_get_sync_groups {

  my $output = "";
  my $is_dp = 'false';

  foreach my $sync_group ( keys %HoA_sync_groups ) {
    $output .= "vrrp_sync_group $sync_group \{\n\tgroup \{\n";
    foreach my $vrrp_instance ( 0 .. $#{ $HoA_sync_groups{$sync_group} } ) {
      $output .= "\t\t$HoA_sync_groups{$sync_group}[$vrrp_instance]\n";
      if ( $HoA_sync_groups{$sync_group}[$vrrp_instance] =~ m/vyatta-dp*/ ) {
         $is_dp = 'true';
      } else {
         $is_dp = 'false';
      }
    }
    $output .= "\t\}\n";

    ## add conntrack-sync part here if configured ##
    if (!defined $connsync) {
      if (defined vrrp_is_connsync_cfg()) {
         $connsync = 'true';
      }
    }
    if ( $is_dp eq 'true' && defined $connsync) {
      $output .= "\tnotify_master \"$sync_dp_script master $sync_group\"\n";
      $output .= "\tnotify_backup \"$sync_dp_script backup $sync_group\"\n";
      $output .= "\tnotify_fault \"$sync_dp_script fault $sync_group\"\n";
    }
    $output .= "\}\n";
  }
  return $output;
}

sub vrrp_read_changes {
  my @lines = ();
  return @lines if !-e $changes_file;
  open( my $FILE, "<", $changes_file ) or die "Error: read $!";
  @lines = <$FILE>;
  close($FILE);
  chomp @lines;
  return @lines;
}

sub vrrp_save_changes {
  my @list = @_;

  my $changes_check_script = "/opt/vyatta/sbin/vrrp-changes-check.sh";
  my $changes_check_link = "/etc/commit/post-hooks.d/50vrrp-changes-check.sh";

  if ( !-e $changes_check_link ) {
    symlink $changes_check_script, $changes_check_link;
  }

  my $num_changes = scalar(@list);
  vrrp_log("saving changes file $num_changes");
  open( my $FILE, ">", $changes_file ) or die "Error: write $!";
  print $FILE join( "\n", @list ), "\n";
  close($FILE);
}

sub get_config_intfs_of_type {
  my ( $config, $intf_type ) = (@_);
  my %list                   = ();

  if ( $config->exists("interfaces $intf_type") ) {
    foreach my $base_intf ( $config->listNodes("interfaces $intf_type") ) {
      $list{$base_intf} = 1;
      if ( $config->exists("interfaces $intf_type $base_intf vif") ) {
        foreach my $vif_intf (
            $config->listNodes("interfaces $intf_type $base_intf vif")
        ) {
          $list{"$base_intf.$vif_intf"} = 1;
        }
      }
    }
  }

  if ( $config->existsOrig("interfaces $intf_type") ) {
    foreach my $base_intf ( $config->listOrigNodes("interfaces $intf_type") ) {
      $list{$base_intf} = 1;
      if ( $config->existsOrig("interfaces $intf_type $base_intf vif") ) {
        foreach my $vif_intf (
            $config->listOrigNodes("interfaces $intf_type $base_intf vif")
        ) {
          $list{"$base_intf.$vif_intf"} = 1;
        }
      }
    }
  }

  return keys %list;
}

sub vrrp_find_changes {

  my @interfaces     = ();
  my @list           = ();
  my $config         = new Vyatta::Config;
  my $vrrp_instances = 0;

  #
  # Check if complete dataplane configuration is deleted
  #
  if ( $config->isDeleted("interfaces dataplane") and
       $config->isDeleted("interfaces bonding") ) {
      return -1;
  }
  #
  # Get list of interfaces that had/will have config.
  # New interface types should be added here.
  #
  push @interfaces, get_config_intfs_of_type($config, "dataplane");
  push @interfaces, get_config_intfs_of_type($config, "bonding");
  foreach my $name ( @interfaces ) {
    my $intf = new Vyatta::Interface($name);
    next unless $intf;
    my $path = $intf->path();
    $config->setLevel($path);
    if ( $config->exists("vrrp vrrp-group") ) {
      my %vrrp_status_hash = $config->listNodeStatus("vrrp vrrp-group");
      my ( $vrrp, $vrrp_status ) = each(%vrrp_status_hash);
      if ( $vrrp_status ne "static" ) {
        push @list, $name;
        vrrp_log("$vrrp_status found $name");
      }
    }

    #
    # Now look for deleted from the origin tree
    #
    $config->setLevel($path);
    if ( $config->isDeleted("vrrp vrrp-group") && $config->isEffective("vrrp vrrp-group")) {
      push @list, $name;
      vrrp_log("Delete found $name");
    }

  }

  my $num = scalar(@list);
  vrrp_log("Start transation: $num changes");
  if ($num) {
    vrrp_save_changes(@list);
  }
  return $num;
}

sub remove_from_changes {
  my $intf = shift;
  # When a VRRP group is configured on a vlan interface the config on both the
  # physical interface and the vlan interface is marked as changed. We remove
  # the vlan line from the change file but we don't remove the physical
  # interface. This can stop keepalived from being restarted with the new
  # configuration.
  $intf =~ s/(.*)\./$1\\\./;
  my $base_intf;
  if (defined $1) {
      $base_intf = $1;
  } else {
      $base_intf = $intf;
  }
  my @lines = vrrp_read_changes();
  if ( scalar(@lines) < 1 ) {

    #
    # we shouldn't get to this point, but try to handle it if we do
    #
    vrrp_log("unexpected remove_from_changes()");
    unlink($changes_file);
    return 0;
  }
  my @new_lines = ();
  foreach my $line (@lines) {
    if ( $line =~ /^$intf$/ or $line =~ /^$base_intf$/ ) {
      vrrp_log("remove_from_changes [$line]");
    } else {
      push @new_lines, $line;
    }
  }

  my $num_changes = scalar(@new_lines);
  if ( $num_changes > 0 ) {
    vrrp_save_changes(@new_lines);
  } else {
    unlink($changes_file);
  }
  return $num_changes;
}

sub vrrp_update_config {

  my @errs   = ();
  my $output;
  my $intf_map_output;

  my $config         = new Vyatta::Config;
  my $vrrp_instances = 0;

  %HoA_sync_groups = ();
  foreach my $name ( getInterfaces() ) {
    my $intf = new Vyatta::Interface($name);
    next unless $intf;
    my $path = $intf->path();
    $config->setLevel($path);
    # The vrrp container in the yang file contains vrrp-group
    # and start-delay, start-delay has a default value meaning that
    # the vrrp container will exist even without any explicit vrrp
    # configuration. Checking for "vrrp vrrp-group" stops keepalived
    # being started with no configuration
    if ( $config->exists("vrrp vrrp-group") ) {

      #
      # keepalived gets real grumpy with interfaces that
      # don't exist, so skip vlans that haven't been
      # instantiated yet (typically occurs at boot up).
      #
      if ( !( -d "/sys/class/net/$name" ) ) {
        push @errs, "$name doesn't exist";
        next;
      }
      my ( $inst_output, $inst_intf_map, @inst_errs ) = keepalived_get_values( $name, $path, 1 );
      if ( scalar(@inst_errs) ) {
        push @errs, @inst_errs;
      } else {
        $output .= $inst_output;
        $intf_map_output .= $inst_intf_map;
        $vrrp_instances++;
      }
    }
  }

  if ( $vrrp_instances > 0 ) {
    my $sync_groups = vrrp_get_sync_groups();
    if ( defined $sync_groups && $sync_groups ne "" ) {
      $output = $sync_groups . $output;
    }
    my $agent_x_socket = get_agent_x_socket();
    my $snmp_socket = "";
    if ($agent_x_socket ne "") {
        $snmp_socket = "\tsnmp_socket $agent_x_socket\n";
    }
    $output = "global_defs {\n\tenable_traps\n\tenable_dbus\n".$snmp_socket."\tenable_snmp_keepalived\n\tenable_snmp_rfc\n}\n" . $output;
    $output = "#\n# autogenerated by $0\n#\n\n" . $output;
    keepalived_write_file( $conf_file, $output );
    keepalived_write_file( $intf_file, $intf_map_output );
  }
  return ( $vrrp_instances, @errs );
}

sub keepalived_write_file {
  my ( $file, $data ) = @_;

  open( my $fh, '>', $file ) || die "Couldn't open $file - $!";
  print $fh $data;
  close $fh;
}

#
# main
#
GetOptions(
  "vrrp-action=s" => \$action,
  "intf=s"        => \$vrrp_intf,
  "group=s"       => \$vrrp_group,
  "vip=s"         => \$vrrp_vip,
  "connsync=s"    => \$connsync,
);

if ( !defined $action ) {
  print "no action\n";
  exit 1;
}

$changes_file = get_changes_file();
$conf_file    = get_conf_file();
$intf_file    = get_intf_file();
%virtual_interfaces = get_virtual_interfaces($conf_file);

#
# run op mode command first
#
if ( $action eq "list-vrrp-intf" ) {
  my @intfs = list_vrrp_intf();
  print join( ' ', @intfs );
  exit 0;
}

if ( $action eq "list-vrrp-group" ) {
  if ( !defined $vrrp_intf ) {
    print "must include interface\n";
    exit 1;
  }
  my @groups = list_vrrp_group($vrrp_intf);
  print join( ' ', @groups );
  exit 0;
}

#
# end of op mode commands
#


#
# This script can be called from two places :
# 1. a vrrp node under one of the interfaces
# 2. service conntrack-sync when conntrack-sync uses VRRP as failover-mechanism
#
# when called from conntrack-sync; we just need to add/remove config 
# for sync-group transition scripts and restart daemon. We do NOT 
# perform any other actions usually done in the update part of this 
# script otherwise 
#

#
# UPDATE action: the logic for "update" is far more complex than it should
# be due to limitations of the cli.  Ideally we would have just one
# end node at the top level 'interfaces' level.  That way we would know that
# all the vif's and bond interfaces have been created and we could call this
# function once to generate the entire keepalived conf file and restart the
# daemon 1 time.  Unfortuately the cli doesn't support nested end nodes, so
# we have to put and end node at every vrrp node and call this function for
# every vrrp instance, but since we only want to start the daemon once we 
# need to keep track of some state.  The first call checks if the "changes"
# file exists, if not it search for all the vrrp instances that have changed
# and adds them to the changes file.  As each instance is processed it is
# removed from changes and when there are no more changes the daemon is
# started/restarted/stopped.  Now since we need to run the script for each 
# instance, we can NOT do "commit" checks in the node.def files since that
# prevents the end node from getting called.  So all the validation needs to
# be in this script, but why not just do all the work once when the changes 
# file is empty?  Well the problem then becomes that when the validation 
# fails, the non-zero exit needs to be associated with the end node otherwise
# the cli will assume it's good push it through to the active config.  So
# we need to do only the validation for the instance being processed and
# then on the last instance generate the full conf file and signal the daemon
# if any changes have been made even if the last instance has a non-zero exit.
#
if ( $action eq "update" ) {
  my $config = new Vyatta::Config;
  my $intf = new Vyatta::Interface($vrrp_intf);
  exit 1 unless $intf;
  my $path = $intf->path();
  $config->setLevel($path);
  # The vrrp container in the yang file contains vrrp-group
  # and start-delay, start-delay has a default value meaning that
  # the vrrp container will exist even without any explicit vrrp
  # configuration. Checking for "vrrp vrrp-group" here to stop the
  # change file being created and causing problems.
  # As update actions are also called for deletions we need to check that
  # there was no configuration in the original config as well. If there is
  # config in the original but not the current then it needs to be deleted.
  # (VCI component should be priority 1 going forward)
  if ( !$config->exists("vrrp vrrp-group") && !$config->existsOrig("vrrp vrrp-group")) {
    exit 0;
  }
  vrrp_log("vrrp update $vrrp_intf")     if defined $vrrp_intf;
  if ( !-e $changes_file ) {
    my $num_changes = vrrp_find_changes();
    if ( $num_changes == 0 ) {
      #
      # Shouldn't happen, but ...
      # - one place were this has been know to occur is if a vif is deleted
      #   that has a vrrp instance under it.  Because the cli doesn't
      #   reverse priorities on delete, then the vrrp under the vif
      #   is gone by the time we get here.
      #
      vrrp_log("unexpected 0 changes");
    }
    if ( $num_changes == -1 ) {
        #
        # This condition is hit when the dataplane configuration
        # is completely cleaned.
        #
        stop_daemon();
        unlink($conf_file);
        unlink($changes_file);
        unlink($intf_file);
        vrrp_log("end transaction\n");
        exit 0;
    }
  }

  if (! defined $intf) {
      die "Error: invalid interface [$vrrp_intf]";
  }
  my ( $inst_output, $intf_mapping, @inst_errs ) = keepalived_get_values( $vrrp_intf, $path );
  if ( scalar(@inst_errs) ) {
    vrrp_log( join( "\n", @inst_errs ) );
    exit 1;
  }
  my $more_changes = remove_from_changes($vrrp_intf);
  vrrp_log("more changes $more_changes");

  if ( $more_changes == 0 ) {
      my ( $vrrp_instances, @errs ) = vrrp_update_config();
      vrrp_log("instances $vrrp_instances");
      if ( $vrrp_instances > 0 ) {
          restart_daemon($conf_file);
          # The changes_file should already be gone by this point, but 
          # this is the "belt & suspenders" approach.
          unlink($changes_file);
          vrrp_log("end transaction\n");
          my $use_vmac = $inst_output =~ /.*use_vmac.*/;
          system("python /opt/vyatta/sbin/vyatta-check-rfc-compatibility.py $use_vmac");
      } elsif ( $vrrp_instances == 0 ) {
          stop_daemon();
          unlink($conf_file);
          unlink($changes_file);
          unlink($intf_file);
          vrrp_log("end transaction\n");
      }
  }
  exit 0;
}

if ( $action eq "update-ctsync" ) {
    vrrp_log("vrrp update conntrack-sync");
    my ( $vrrp_instances, @errs ) = vrrp_update_config();
    vrrp_log("instances $vrrp_instances");
    if ($vrrp_instances > 0) {
        restart_daemon($conf_file);
    }
    exit 0;
}

if ( $action eq "delete" ) {
  if ( !defined $vrrp_intf || !defined $vrrp_group ) {
    print "must include interface & group";
    exit 1;
  }
  vrrp_log("vrrp delete $vrrp_intf $vrrp_group");
  my $state_file = get_state_file( $vrrp_intf, $vrrp_group );
  unlink($state_file);
  exit 0;
}

exit 0;

# end of file
