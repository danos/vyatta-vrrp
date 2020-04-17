#
# Module: VyattaKeepalived.pm
#
# **** License ****
#
# Copyright (c) 2017-2019 AT&T Intellectual Property.
# All rights reserved.
#
# Copyright (c) 2014-2017 by Brocade Communications Systems, Inc.
# All rights reserved.
#
# This code was originally developed by Vyatta, Inc.
# Portions created by Vyatta are Copyright (C) 2009 Vyatta, Inc.
# All Rights Reserved.
#
# Author: Stig Thormodsrud
# Date: October 2007
# Description: Common keepalived definitions/funcitions
#
# SPDX-License-Identifier: GPL-2.0-only
#
# **** End License ****
#
package Vyatta::Keepalived;
use strict;
use warnings;

our @EXPORT = qw(get_conf_file get_state_script get_state_file
  get_intf_file vrrp_log vrrp_get_init_state
  get_changes_file start_daemon restart_daemon stop_daemon
  vrrp_get_config list_vrrp_intf list_vrrp_group
  list_vrrp_sync_group list_all_vrrp_sync_grps
  list_vrrp_sync_group_members
  vrrp_get_primary_addr get_agent_x_socket is_running);
use base qw(Exporter);

use Vyatta::Config;
use Vyatta::Interface;
use Vyatta::Misc;
use POSIX;

my $keepalived_conf      = '/etc/keepalived/keepalived.conf';
my $sbin_dir             = '/opt/vyatta/sbin';
my $state_transition     = "$sbin_dir/vyatta-vrrp-state.pl";
my $keepalived_pid       = '/var/run/keepalived.pid';
my $state_dir            = '/var/run/vrrpd';
my $vrrp_log             = "$state_dir/vrrp.log";
my $changes_file         = "$state_dir/changes";
my $snmpd_conf           = '/etc/snmp/snmpd.conf';
my $intf_mapping         = "$state_dir/vrrp_intf.map";
my $systemd_default_file = '/etc/default/keepalived';

sub sys_logger {
    my ($msg) = @_;
    my $FACILITY = "local7";
    my $LEVEL = "debug";
    my $TAG = "vyatta-vrrp";
    my $LOGCMD = "logger -t $TAG -p $FACILITY.$LEVEL";
    system("$LOGCMD '$msg'.");
    return;
}

sub vrrp_log {
    my $timestamp = strftime( "%Y%m%d-%H:%M.%S", localtime );
    open my $fh, '>>', $vrrp_log
      or die "Can't open $vrrp_log:$!";
    print $fh "$timestamp: ", @_, "\n";
    close $fh;
    sys_logger(@_);
}

# Get the agentXSocket value stored in /etc/snmp/snmpd.conf
# otherwise return an empty string
sub get_agent_x_socket {

    # Default to this value for agentX so we always try to connect to something.
    my $socket_value = "tcp:localhost:705:1";

    if ( !-e $snmpd_conf ) {
        return $socket_value;
    }
    open( my $fh, '<', $snmpd_conf )
      or die "Could not open file: '$snmpd_conf' $!";
    while (<$fh>) {
        if ( $_ =~ /agentXSocket\s(.*)/ ) {

            # Add routing ID 1 (default RID) to the socket value. Without this
            # we fail to connect to the snmpd when we use a vrf enabled image.
            $socket_value = "$1:1";
            last;
        }
    }
    close($fh) or warn "Unable to close the file handle: $!";
    return $socket_value;
}

sub is_running {
    if ( -f $keepalived_pid ) {
        my $pid = `cat $keepalived_pid`;
        $pid =~ s/\s+$//;    # chomp doesn't remove nl
        my $ps = `ps -p $pid -o comm=`;

        if ( defined($ps) && $ps ne "" ) {
            return 1;
        }
    }
    return 0;
}

sub start_daemon {
    my ($conf) = @_;

    my $snmp_socket         = get_agent_x_socket();
    my $default_file_string = "#Options to pass to keepalvied\n";
    $default_file_string .=
      "# DAEMON_ARGS are appended to the keepalived command-line\n";
    my $cmd .=
      'DAEMON_ARGS="--snmp --log-facility=7 --log-detail --dump-conf -x';
    $cmd .= " --use-file $conf --release-vips";
    if ( $snmp_socket ne "" ) {
        $cmd .= " --snmp-agent-socket $snmp_socket";
    }
    $cmd .= '"' . "\n";
    $default_file_string .= $cmd;
    open( my $fh, '>', $systemd_default_file )
      or die "Can't open $systemd_default_file:$!";
    print $fh $default_file_string;
    close $fh;
    system("service keepalived start");
    vrrp_log("start_daemon");
}

sub stop_daemon {
    if ( is_running() ) {
        system("service keepalived stop");
        vrrp_log("stop_daemon");
    }
    else {
        vrrp_log("stop daemon called while not running");
    }
}

sub restart_daemon {
    my ($conf) = @_;

    if ( is_running() ) {
        system("service keepalived reload");
        vrrp_log("restart_deamon");
    }
    else {
        start_daemon($conf);
    }
}

sub get_conf_file {
    return $keepalived_conf;
}

sub get_intf_file {
    return $intf_mapping;
}

sub get_state_script {
    return $state_transition;
}

sub get_changes_file {
    system("mkdir $state_dir") if !-d $state_dir;
    return $changes_file;
}

sub get_state_file {
    my ( $vrrp_intf, $vrrp_group ) = @_;

    system("mkdir $state_dir") if !-d $state_dir;
    my $file = "$state_dir/vrrpd_" . "$vrrp_intf" . "_" . "$vrrp_group.state";
    return $file;
}

sub get_master_file {
    my ( $vrrp_intf, $vrrp_group ) = @_;

    my $file = "$state_dir/vrrpd_" . "$vrrp_intf" . "_" . "$vrrp_group.master";
    return $file;
}

sub alphanum_split {
    my ($str) = @_;
    my @list = split m/(?=(?<=\D)\d|(?<=\d)\D)/, $str;
    return @list;
}

sub natural_order {
    my ( $a, $b ) = @_;
    my @a = alphanum_split($a);
    my @b = alphanum_split($b);

    while ( @a && @b ) {
        my $a_seg = shift @a;
        my $b_seg = shift @b;
        my $val;
        if ( ( $a_seg =~ /\d/ ) && ( $b_seg =~ /\d/ ) ) {
            $val = $a_seg <=> $b_seg;
        }
        elsif ( ( $a_seg eq '.' ) && ( $b_seg eq '_' ) ) {
            return 1;
        }
        else {
            $val = $a_seg cmp $b_seg;
        }
        if ( $val != 0 ) {
            return $val;
        }
    }
    return @a <=> @b;
}

sub intf_sort {
    my @a = @_;
    my @new_a = sort { natural_order( $a, $b ) } @a;
    return @new_a;
}

sub get_state_files {
    my ( $intf, $group ) = @_;

    opendir my $sdir, $state_dir
      or die "Can't open $state_dir: $!\n";

    my @state_files;
    if ( $group eq "all" ) {
        @state_files = grep { /^vrrpd_$intf.*\.state$/ } readdir($sdir);
    }
    else {
        my $intf_group = $intf . "_" . $group . ".state";
        @state_files = grep { /^vrrpd_$intf_group$/ } readdir($sdir);
    }
    close $sdir;

    @state_files = intf_sort(@state_files);
    foreach my $i ( 0 .. $#state_files ) {
        $state_files[$i] = "$state_dir/$state_files[$i]";
    }
    chomp @state_files;
    return @state_files;
}

sub vrrp_get_primary_addr {
    my ($intf) = @_;

    my $path;
    my $config    = new Vyatta::Config;
    my $interface = new Vyatta::Interface($intf);
    die "Unknown interface type: $intf" unless $interface;

    $path = $interface->path();
    $config->setLevel($path);

    # don't use getIP() to get IP addresses because we only
    # want configured addresses, not vrrp VIP addresses.
    my @addrs = ();
    if ( $config->inSession ) {
        @addrs = $config->returnValues('address');
    }
    else {
        @addrs = $config->returnOrigValues('address');
    }
    my $primary_addr = shift @addrs;

    if ( defined $primary_addr
        and $primary_addr =~ m/(\d+\.\d+\.\d+\.\d+)\/\d+/ )
    {
        $primary_addr = $1;    # strip /mask
    }
    return $primary_addr;
}

#
# this is meant to be called from op mode, so Orig functions are used.
#
sub vrrp_get_config {
    my ( $intf, $group ) = @_;

    my $path;
    my $config    = new Vyatta::Config;
    my $interface = new Vyatta::Interface($intf);
    die "Unknown interface type: $intf" unless $interface;

    my $primary_addr = vrrp_get_primary_addr($intf);
    if ( !defined $primary_addr or $primary_addr eq 'dhcp' ) {
        $primary_addr = "0.0.0.0";
    }

    $path = $interface->path();
    $config->setLevel("$path vrrp vrrp-group $group");
    my $source_addr = $config->returnOrigValue("hello-source-address");
    $primary_addr = $source_addr if defined $source_addr;

    my @vips     = $config->returnOrigValues("virtual-address");
    my $priority = $config->returnOrigValue("priority");
    if ( !defined $priority ) {
        $priority = 100;
    }
    my $preempt = $config->returnOrigValue("preempt");
    if ( !defined $preempt ) {
        $preempt = "true";
    }
    my $accept = $config->returnOrigValue("accept");
    $accept = "false" unless ( defined $accept );

    my $advert_int = $config->returnOrigValue("advertise-interval");
    if ( !defined $advert_int ) {
        $advert_int = 1;
    }
    my $fast_advert_int = $config->returnOrigValue("fast-advertise-interval");
    $fast_advert_int = "1000" unless ( defined $fast_advert_int );

    my $vmac_interface = $config->existsOrig("rfc-compatibility");
    $vmac_interface = "0" unless ( defined $vmac_interface );

    if ( $vmac_interface && $primary_addr eq "0.0.0.0" ) {
        $primary_addr = $vips[0];
        $primary_addr =~ s/(.*?)\/.*/$1/;
    }

    my $rfc_version = $config->returnOrigValue("version");
    $rfc_version = "2" unless ( defined $rfc_version );

    $config->setLevel("$path vrrp vrrp-group $group authentication");
    my $auth_type = $config->returnOrigValue("type");
    if ( !defined $auth_type ) {
        $auth_type = "none";
    }

    return (
        $primary_addr, $priority,       $preempt, $advert_int,
        $auth_type,    $vmac_interface, @vips,    $fast_advert_int,
        $rfc_version,  $accept
    );
}

sub snoop_for_master {
    my ( $intf, $group, $vip, $timeout ) = @_;

    my ( $cap_filt, $dis_filt, $options, $cmd );

    my $file = get_master_file( $intf, $group );

    # remove mask if vip has one
    if ( $vip =~ /([\d.]+)\/\d+/ ) {
        $vip = $1;
    }

    #
    # set up common tshark parameters
    #
    $cap_filt = "-f \"host 224.0.0.18";
    $dis_filt = "-R \"vrrp.virt_rtr_id == $group and vrrp.ip_addr == $vip\"";
    $options  = "-a duration:$timeout -p -i$intf -c1 -T pdml";

    my $auth_type = ( vrrp_get_config( $intf, $group ) )[4];
    if ( lc($auth_type) ne "ah" ) {
        #
        # the vrrp group is the 2nd byte in the vrrp header
        #
        $cap_filt .= " and proto VRRP and vrrp[1:1] = $group\"";
        $cmd = "tshark $options $cap_filt $dis_filt";
        system("$cmd > $file 2> /dev/null");
    }
    else {
        #
        # if the vrrp group is using AH authentication, then the proto will be
        # AH (0x33) instead of VRRP (0x70). So try snooping for AH and
        # look for the vrrp group at byte 45 (ip_header=20, ah=24)
        #
        $cap_filt .= " and proto 0x33 and ip[45:1] = $group\"";
        $cmd = "tshark $options $cap_filt $dis_filt";
        system("$cmd > $file 2> /dev/null");
    }
}

sub vrrp_state_parse {
    my ($file) = @_;

    $file =~ s/\s+$//;    # chomp doesn't remove nl
    if ( -f $file ) {
        my $line = `cat $file`;
        chomp $line;
        my ( $start_time, $intf, $group, $state, $ltime ) = split( ' ', $line );
        return ( $start_time, $intf, $group, $state, $ltime );
    }

    # else return undefined
}

sub vrrp_get_init_state {
    my ( $intf, $group, $vips, $preempt ) = @_;

    my $init_state;
    if ( is_running() ) {
        my @state_files = get_state_files( $intf, $group );
        chomp @state_files;
        if ( scalar(@state_files) > 0 ) {
            my ( $start_time, $f_intf, $f_group, $state, $ltime ) =
              vrrp_state_parse( $state_files[0] );
            if ( $state eq "master" ) {
                $init_state = 'MASTER';
            }
            else {
                $init_state = 'BACKUP';
            }
            return $init_state;
        }

        # fall through to logic below
    }

    # start as backup by default
    $init_state = 'BACKUP';

    return $init_state;
}

sub list_vrrp_intf {
    my ($val_func) = @_;
    my $config     = new Vyatta::Config;
    my @intfs      = ();

    foreach my $name ( getInterfaces() ) {
        my $intf = new Vyatta::Interface($name);
        next unless $intf;
        my $path = $intf->path();
        $config->setLevel($path);
        if ( defined $val_func ) {
            push @intfs, $name if $config->$val_func("vrrp");
        }
        else {
            push @intfs, $name if $config->existsOrig("vrrp");
        }
    }

    return @intfs;
}

sub list_vrrp_group {
    my ( $name, $val_func ) = @_;
    my $config = new Vyatta::Config;
    my $path;

    my $intf = new Vyatta::Interface($name);
    next unless $intf;
    $path = $intf->path();
    $path .= " vrrp vrrp-group";
    $config->setLevel($path);
    my @groups = ();
    if ( defined $val_func ) {
        @groups = $config->$val_func();
    }
    else {
        @groups = $config->listOrigNodes();
    }
    return @groups;
}

sub list_vrrp_sync_group {
    my ( $name, $group, $val_func ) = @_;
    my $config = new Vyatta::Config;
    my $path;

    my $intf = new Vyatta::Interface($name);
    next unless $intf;
    $path = $intf->path();
    $path .= " vrrp vrrp-group $group sync-group";
    $config->setLevel($path);
    my $sync_group = undef;
    if ( defined $val_func ) {
        $sync_group = $config->$val_func();
    }
    else {
        $sync_group = $config->returnOrigValue();
    }
    return $sync_group;
}

sub list_all_vrrp_sync_grps {
    my @sync_grps  = ();
    my @vrrp_intfs = list_vrrp_intf();
    foreach my $vrrp_intf (@vrrp_intfs) {
        my @vrrp_groups = list_vrrp_group($vrrp_intf);
        foreach my $vrrp_group (@vrrp_groups) {
            my $sync_grp = list_vrrp_sync_group( $vrrp_intf, $vrrp_group );
            if ( defined $sync_grp ) {

                # add to sync_grps if not already there
                if ( scalar( grep( /^$sync_grp$/, @sync_grps ) ) == 0 ) {
                    push( @sync_grps, $sync_grp );
                }
            }
        }
    }
    return @sync_grps;
}

sub list_vrrp_sync_group_members {
    my ($sync_grp_match) = @_;
    my @members          = ();
    my @vrrp_intfs       = list_vrrp_intf();
    foreach my $vrrp_intf (@vrrp_intfs) {
        my @vrrp_groups = list_vrrp_group($vrrp_intf);
        foreach my $vrrp_group (@vrrp_groups) {
            my $sync_grp = list_vrrp_sync_group( $vrrp_intf, $vrrp_group );
            my $is_active = vrrp_group_is_active( $vrrp_intf, $vrrp_group );
            if (    defined $sync_grp
                and $sync_grp eq $sync_grp_match
                and $is_active )
            {
                push @members, 'vyatta-' . $vrrp_intf . '-' . $vrrp_group;
            }
        }
    }
    return @members;
}

sub vrrp_group_is_active {
    my ( $name, $group ) = @_;
    my $config = new Vyatta::Config;
    my $path;
    my $is_active = 1;

    my $intf = new Vyatta::Interface($name);
    next unless $intf;
    $path = $intf->path();
    $path .= " vrrp vrrp-group $group";
    $config->setLevel($path);
    if ( $config->existsOrig("disable") ) {
        $is_active = 0;
    }
    return $is_active;
}
1;

#end of file
