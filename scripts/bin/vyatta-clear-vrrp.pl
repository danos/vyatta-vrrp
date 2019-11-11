#!/usr/bin/perl
#
# Module: vyatta-clear-vrrp.pl
# 
# **** License ****
#
# Copyright (c) 2019 by AT&T Intellectual Property.
# All rights reserved.
#
# Copyright (c) 2014 by Brocade Communications Systems, Inc.
# All rights reserved.
#
# This code was originally developed by Vyatta, Inc.
# Portions created by Vyatta are Copyright (C) 2007-2009 Vyatta, Inc.
# All Rights Reserved.
# 
# Author: Stig Thormodsrud
# Date: May 2008
# Description: Script to clear vrrp
# 
# SPDX-License-Identifier: GPL-2.0-only
#
# **** End License ****

use lib '/opt/vyatta/share/perl5/';
use Vyatta::Keepalived;
use Vyatta::Misc;
use Vyatta::VRRP::OPMode;

use Net::IP;
use Net::DBus;
use Try::Tiny;
use Getopt::Long;
use Sys::Syslog qw(:standard :macros);

use strict;
use warnings;

my $conf_file = get_conf_file();
my $bus = Net::DBus->system;
my $dbus_service;
my $dbus_object;
try {
  $dbus_service = $bus->get_service("org.keepalived.Vrrp1");
};


sub keepalived_write_file {
    my ($file, $data) = @_;

    open(my $fh, '>', $file) || die "Couldn't open $file - $!";
    print $fh $data;
    close $fh;
}

#
# main
#
my ($action, $vrrp_intf, $vrrp_group);

GetOptions("vrrp-action=s" => \$action,
	   "intf=s"        => \$vrrp_intf,
	   "group=s"       => \$vrrp_group);

if (! defined $action) {
    print "no action\n";
    exit 1;
}

openlog($0, '', LOG_USER);
my $login = getlogin();

#
# clear_process
#
if ($action eq 'clear_process') {
    syslog('warning', "clear vrrp process requested by $login");
    if (Vyatta::Keepalived::is_running()) {
	print "Restarting VRRP...\n";
	restart_daemon(get_conf_file());
    } else {
	print "Starting VRRP...\n";
	start_daemon(get_conf_file());
    }
    exit 0;
}

#
# clear_master
#
if ($action eq 'clear_master') {
    
    #
    # Use DBus method to reset a group to backup state
    # Note: if the instance if preempt=true, then it may immediately
    # try to become master again.
    #

    if (! defined $vrrp_intf || ! defined $vrrp_group) {
        print "must include interface & group\n";
        exit 1;
    }

    my $instance = 'vyatta-' . "$vrrp_intf" . '-' . "$vrrp_group";
    my %data_hash = ();
    process_data(\%data_hash);
    if (!defined($data_hash{instances}->{$vrrp_intf}->{$vrrp_group})) {
      print "Invalid interface/group [$vrrp_intf][$vrrp_group] (group may be disabled)\n";
      exit 1;
    }
    my $state = $data_hash{instances}->{$vrrp_intf}->{$vrrp_group}->{state};
    my $af_type;
    my $vip = $data_hash{instances}->{$vrrp_intf}->{$vrrp_group}->{'vips'}[0];
    my ($ip, $len) = Net::IP::ip_splitprefix($vip);
    if ( Net::IP::ip_is_ipv6($ip) ) {
        $af_type = "IPv6"
    } else {
        $af_type = "IPv4"
    }

    if ($state ne 'MASTER') {
        print "vrrp group $vrrp_group on $vrrp_intf is already in backup\n";
        exit 1;
    }

    syslog('warning', "clear vrrp master [$instance] requested by $login");
    Vyatta::Keepalived::vrrp_log("vrrp clear_master $vrrp_intf $vrrp_group");

    my $sync_group = list_vrrp_sync_group($vrrp_intf, $vrrp_group);
    my @instances = ();
    if (defined($sync_group)) {
        print "vrrp group $vrrp_group on $vrrp_intf is in sync-group " 
              . "$sync_group\n";
        @instances = list_vrrp_sync_group_members($sync_group);
    } else {
        push @instances, $instance;
    }

    foreach my $inst (@instances) {
        $inst =~ m/vyatta-(.*?)-(.*)/;
        my ($inst_intf, $inst_vrid) = ($1, $2);
        if (!defined($data_hash{instances}->{$inst_intf}->{$inst_vrid})) {
            continue;
        }
        print "Forcing $inst to BACKUP...\n";
        if ($data_hash{instances}->{$inst_intf}->{$inst_vrid}->{'preempt'} eq "enabled") {
            print "Warning: $instance is in preempt mode";
            print " and may retake master\n";
        }
    }
    # A . in a dbus path is invalid. Vif interfaces must be converted to use _;
    $vrrp_intf =~ s/\./_/g;
    $dbus_object = $dbus_service->get_object("/org/keepalived/Vrrp1/Instance/$vrrp_intf/$vrrp_group/$af_type");
    $dbus_object->ResetMaster;
}

exit 0;

# end of file
