#!/usr/bin/perl
# 
# **** License ****
# 
# Copyright (c) 2019 AT&T Intellectual Property.
# All rights reserved.
# 
# Copyright (c) 2014-2015 by Brocade Communications Systems, Inc.
# All rights reserved.
#
# This code was originally developed by Vyatta, Inc.
# Portions created by Vyatta are Copyright (C) 2007-2012 Vyatta, Inc.
# All Rights Reserved.
# 
# Author: John Southworth
# Date: May 2012  
# Description: Process operational data from keepalived
# 
# SPDX-License-Identifier: GPL-2.0-only
#
# **** End License ****
#

use strict;
use warnings;
use lib "/opt/vyatta/share/perl5";

use Getopt::Long;
use Vyatta::VRRP::OPMode;
use Vyatta::Keepalived qw(is_running);
use Sort::Versions;
use v5.10;

my ($show, $intf, $vrid, $sync);
my $quiet = "";
GetOptions("show=s" => \$show,
           "intf=s" => \$intf,
           "vrid=s" => \$vrid,
           "sync=s" => \$sync,
           "quiet"  => \$quiet
          );

sub list_vrrp_intf {
  my $intf = shift; 
  my $hash = {};
  process_data $hash;
  if ($intf) {
    printf "%s\n", join " ", sort {versioncmp($a, $b)} keys(%{$hash->{instances}->{$intf}});
  } else {
    printf "%s\n", join " ", sort {versioncmp($a, $b)} keys(%{$hash->{instances}});
  }
}

sub list_vrrp_groups {
  my $intf = shift; 
  my $group = {};
  my $hash = {};
  process_data $hash;
  foreach my $group (sort {versioncmp($a, $b)} keys(%{$hash->{instances}->{$intf}})) {
    printf "%s\n", join " ", sort {versioncmp($a, $b)} $group;
  }
}

sub list_vrrp_sync_groups {
    my $hash = {};
    process_data $hash;
    printf "%s\n", join " ", sort {versioncmp($a, $b)} keys(%{$hash->{'sync-groups'}});
}

sub show_vrrp_summary {
  my ($intf, $vrid) = @_;
  my $hash = {};
  process_data $hash;
  return if (check_intf($hash, $intf, $vrid));
  print_summary $hash, $intf, $vrid;
}

sub show_vrrp_interfaces {
  my ($intf, $vrid) = @_;
  my $hash = {};
  process_data $hash;
  return if (check_intf($hash, $intf, $vrid));
  print_interfaces $hash, $intf, $vrid;
}

sub show_vrrp_stats {
  my ($intf, $vrid) = @_;
  my $hash = {};
  process_stats $hash;
  return if (check_intf($hash, $intf, $vrid));
  print_stats $hash, $intf, $vrid;
}

sub show_vrrp_detail {
  my ($intf, $vrid) = @_;
  my $hash = {};
  process_data $hash;
  return if (check_intf($hash, $intf, $vrid));
  print_detail $hash, $intf, $vrid;
}

sub show_vrrp_sync_groups {
  my $sync = shift;
  my $hash = {};
  process_data $hash;
  if ($sync && !exists($hash->{'sync-groups'}->{$sync})){
    print "Sync-group: $sync does not exist\n";
    return;
  }
  print_sync $hash, $sync;
}

if (!Vyatta::Keepalived::is_running()) {
    Vyatta::VRRP::OPMode::vrrp_norun() if !$quiet;
    exit;
}
if ($show eq 'summary') {
    show_vrrp_summary $intf, $vrid;
} elsif ($show eq 'interfaces') {
    show_vrrp_interfaces $intf, $vrid;
} elsif ($show eq 'detail') {
    show_vrrp_detail $intf, $vrid;
} elsif ($show eq 'stats') {
    show_vrrp_stats $intf, $vrid;
} elsif ($show eq 'sync') {
    show_vrrp_sync_groups $sync;
} elsif ($show eq 'interface') {
    list_vrrp_intf $intf;
} elsif ($show eq 'syncs') {
    list_vrrp_sync_groups;
} elsif ($show eq 'groups') {
    list_vrrp_groups $intf;
} else{
    exit;
}



