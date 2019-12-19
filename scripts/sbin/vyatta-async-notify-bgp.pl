#!/usr/bin/perl
#
# Module: vyatta-vrrp-state.pl
#
# **** License ****
# Copyright (c) 2019 AT&T Intellectual Property.
# All rights reserved.
#
# Copyright (c) 2015 by Brocade Communications Systems, Inc.
# All rights reserved.
#
#
# Date: September 2015
#
# Description: When 'notify bgp' is configured on VRRP and the equivalent
# 'vrrp-failover' config is added on the BGP side, BGP gets notifications
# when VRRP instances change state. However, if BGP gets deleted some time
# later, since it doesn't retain VRRP state information, when the
# 'vrrp-failover' is re-applied, BGP will call this script which triggers
# a new notification to be sent, which will restore state information in
# BGP.
#
# SPDX-License-Identifier: GPL-2.0-only
#
# **** End License ****
#

use strict;
use warnings;

use lib "/opt/vyatta/share/perl5/";
use Vyatta::VRRP::OPMode;
use Vyatta::Keepalived;
use Scalar::Util;
use POSIX;

sub vrrp_bgp_async_notify {
    my ( $vrrp_group, $intf ) = @_;

    my $try = 0;

    if( (defined $vrrp_group) and (not defined $intf)) {
        if(Scalar::Util::looks_like_number($vrrp_group)) {
            $intf = get_associated_intf($vrrp_group);
            if(defined $intf) {
                $try = 1;
            }
        }
    }

    if( (defined $vrrp_group) and (defined $intf)) {
        $try = 1;
    }

    my $script = "/opt/vyatta/sbin/notify-bgp";

    if($try) {
        my $state = get_state($intf, $vrrp_group);

        if (not defined $state) {
            vrrp_log("Failed to get state");
        }

        elsif ($state eq 'MASTER') {
            vrrp_log("vrrp_instance=vyatta-$intf-$vrrp_group, state=master");
            system($script, "instance", "vyatta-$intf-$vrrp_group", "master");
        }

        elsif ($state eq 'BACKUP') {
            vrrp_log("vrrp_instance=vyatta-$intf-$vrrp_group, state=backup");
            system($script, "instance", "vyatta-$intf-$vrrp_group", "backup");
        }

        elsif ($state eq 'FAULT') {
            vrrp_log("vrrp_instance=vyatta-$intf-$vrrp_group, state=fault");
            system($script, "instance", "vyatta-$intf-$vrrp_group", "fault");
        }

        else {
            vrrp_log("Unknown state for vyatta-$intf-$vrrp_group");
        }
    }
    else {
        vrrp_log("Invalid argument(s)");
    }
}

if (Vyatta::Keepalived::is_running()) {
    my @vrrp_intfs = list_vrrp_intf();
    foreach my $vrrp_intf (@vrrp_intfs) {
        my @vrrp_groups = list_vrrp_group($vrrp_intf);
        foreach my $vrrp_group (@vrrp_groups) {
            vrrp_bgp_async_notify ($vrrp_group, $vrrp_intf);
        }
   }
}

exit 0;
