#! /usr/bin/perl
#
# Module: vyatta-log-vrrp-transition.pl
#
# **** License ****
#
# Copyright (c) 2019 AT&T Intellectual Property.
# All rights reserved.
# Copyright (c) 2015 by Brocade Communications Systems, Inc.
# All rights reserved.
#
# Author: Anthony Dempsey
# Date: April 2015
# Description: Script to log a vrrp state transition.
#
# SPDX-License-Identifier: GPL-2.0-only
#
# **** End License ****
#

use strict;
use warnings;
use Vyatta::Keepalived;

my $vrrp_state = $ARGV[0];
my $vrrp_intf  = $ARGV[1];
my $vrrp_group = $ARGV[2];
# transition interface will contain the vmac interface
# when one is present and the vrrp interface when one is not
my $transition_intf = $ARGV[3]; 
my $vrrp_transitionscript = $ARGV[4];
my @vrrp_vips;
foreach my $arg (5 .. $#ARGV) {
    push @vrrp_vips, $ARGV[$arg];
}

Vyatta::Keepalived::vrrp_log("\n");
Vyatta::Keepalived::vrrp_log("Running test transition script.");
Vyatta::Keepalived::vrrp_log("Received the following arguments.");

Vyatta::Keepalived::vrrp_log("State: $vrrp_state");
Vyatta::Keepalived::vrrp_log("Interface: $vrrp_intf");
Vyatta::Keepalived::vrrp_log("Group: $vrrp_group");
Vyatta::Keepalived::vrrp_log("Completed transition script");
Vyatta::Keepalived::vrrp_log("\n");

