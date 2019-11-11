# 
# Module: Vyatta::VRRP::OPMode
# 
# **** License ****
#
# Copyright (c) 2019 AT&T Intellectual Property.
# All rights reserved.
#
# Copyright (c) 2014 by Brocade Communications Systems, Inc.
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

package Vyatta::VRRP::OPMode;
use strict;
use warnings;
our @EXPORT = qw(get_pid process_data process_stats print_interfaces print_summary print_stats print_sync print_detail check_intf get_state get_associated_intf);
use base qw(Exporter);

use Sort::Versions;
use Net::DBus;
use Try::Tiny;

my $PIDFILE='/var/run/vrrp.pid';
my $DATAFILE='/tmp/keepalived.data';
my $STATSFILE='/tmp/keepalived.stats';

my $bus = Net::DBus->system;
my $dbus_service;
my $dbus_object;

try {
  $dbus_service = $bus->get_service("org.keepalived.Vrrp1");
  $dbus_object = $dbus_service->get_object("/org/keepalived/Vrrp1/Vrrp");
};

sub vrrp_norun {
  printf("VRRP is not running");
  exit;
}

sub get_pid {
  open my $PIDF, '<', $PIDFILE or vrrp_norun;
  my $PID=<$PIDF>;
  close $PIDF;
  return $PID;
}

sub trim {
  my $string = shift;
  $string =~ s/^\s+//;
  $string =~ s/\s+$//;
  return $string;
}

sub conv_name {
  my $name = shift;
  $name = trim $name;
  $name = lc $name;
  $name =~ s/\s/-/g; 
  return $name;
}

sub add_to_datahash {
  my ($dh, $interface, $instance, $in_sync, $name, $val) = @_;
  $name = conv_name $name;
  if ($in_sync) {
    if ($name eq 'monitor'){
      $dh->{'sync-groups'}->{$instance}->{$name} = 
        [ $dh->{'sync-groups'}->{$instance}->{$name} ? 
          @{$dh->{'sync-groups'}->{$instance}->{$name}} : (),
          $val
        ];
    } else {
      $dh->{'sync-groups'}->{$instance}->{$name} = $val;
    }
  } else {
     $dh->{'instances'}->{$interface}->{$instance}->{$name} = $val;
  }
}

sub wait_for_data {
  my $file = shift;
  my $curtime = time();
  my $timestamp;
  my $attempts = 0;
  while ($attempts < 4)
  {
    ++$attempts;
    if (! -e $file){
      sleep(1);
      next;
    }
    $timestamp = (stat($file))[9];
    if ($timestamp < $curtime) {
      sleep(1);
    } else {
      last;
    }
  }
  if (! -e $file){
    printf "VRRP process not responding to request for operational data\n";
    exit(1);
  }
  if ($timestamp < $curtime){
      printf "VRRP process not responding to request for operational data\n";
      printf "  The data displayed may be out of date\n";
      printf "  This is normally due to an in progress transition\n";
  }
}

sub process_data {
  my ($dh) = @_;
  my (
      $instance, $interface, $in_sync, $in_vip,
      $track_ifp, $if_name, $if_state, $if_weight,
      $track_pm, $monitor, $policy, $pm_state, $pm_weight
  );
  if ($dbus_object){
	 $dbus_object->PrintData();
  } else {
	kill 'SIGUSR1', get_pid();
  }
  wait_for_data($DATAFILE);
  open my $DATA, '<',  $DATAFILE;
  while (<$DATA>)
  {
    m/VRRP Instance = vyatta-(.*?)-(.*)/ && do {
      $interface = $1;
      $instance = $2;
      $in_sync = undef;
      $in_vip = undef;
      $dh->{'instances'}->{$interface}->{$instance} = {};
      next;
    };
    m/VRRP Sync Group = (.*?), (.*)/ && do {
      $instance = $1;
      $interface = undef;
      $in_vip = undef;
      my $state = $2;
      $in_sync = 1;
      add_to_datahash $dh, $interface, $instance, $in_sync, 'state', $state;
      next;
    };
    if ($in_vip){
      m/(.*?) dev (.*)/ && do {
        my $inst = $dh->{'instances'}->{$interface}->{$instance};
        $inst->{vips} = [ $inst->{vips} ? @{ $inst->{vips} } : (), trim $1 ];
      };
    }
    if ($track_pm) {
        m/Monitor = (.*)/ && do {
            $monitor = $1;
            next;
        };
        m/Policy = (.*)/ && do {
            $policy = $1;
            next;
        };
        m/Status = (.*)/ && do {
            $dh->{'instances'}->{$interface}->{$instance}->{'pms'}
            ->{$monitor}->{$policy}->{'state'} = $1;
             next;
        };
        m/Weight = (.*)/ && do {
            $dh->{'instances'}->{$interface}->{$instance}->{'pms'}->{$monitor}
              ->{$policy}->{'weight'} = $1;
        };
    }
    if ($track_ifp) {
        m/Name = (.*)/ && do {
            $if_name = $1;
            next;
        };
        m/is (.*)/ && do {
            if ( $1 ne 'RUNNING' ) {
                $if_state = $1;
                $dh->{'instances'}->{$interface}->{$instance}->{'ifps'}
                 ->{$if_name}->{'state'} = $1;
                 next;
            }
        };
        m/weight = (.*)/ && do {
            $if_weight = $1;
            $dh->{'instances'}->{$interface}->{$instance}->{'ifps'}->{$if_name}
              ->{'weight'} = $1;
        };
    };
    m/(.*?) = (.*)/ && do {
      $in_vip = undef;
      add_to_datahash $dh, $interface, $instance, $in_sync, $1, $2;
      m/Virtual IP/ && do {$in_vip = 1; $track_ifp = undef; $track_pm = undef};
      m/Tracked interface/ && do {$track_ifp = 1; $in_vip = undef; $track_pm = undef;};
      m/Tracked path-monitors/ && do {$track_pm = 1; $in_vip = undef; 
          $track_ifp = undef;};
      next;
    };
  }
  close $DATA;
}

sub elapse_time {
    my ($start, $stop) = @_;
    $start =~ s/(\d+).*/$1/;

    my $seconds   = $stop - $start;
    my $string    = '';
    my $secs_min  = 60;
    my $secs_hour = $secs_min  * 60;
    my $secs_day  = $secs_hour * 24;
    my $secs_week = $secs_day  * 7;

    my $weeks = int($seconds / $secs_week);
    if ($weeks > 0 ) {
        $seconds = int($seconds % $secs_week);
        $string .= $weeks . "w";
    }
    my $days = int($seconds / $secs_day);
    if ($days > 0) {
        $seconds = int($seconds % $secs_day);
        $string .= $days . "d";
    }
    my $hours = int($seconds / $secs_hour);
    if ($hours > 0) {
        $seconds = int($seconds % $secs_hour);
        $string .= $hours . "h";
    }
    my $mins = int($seconds / $secs_min);
    if ($mins > 0) {
        $seconds = int($seconds % $secs_min);
        $string .= $mins . "m";
    }
    $string .= $seconds . "s";

    return $string;
}

sub find_sync {
   my ($intf, $vrid, $dh)  = @_;
   my $instance = "vyatta-$intf-$vrid";
   foreach my $sync (sort {versioncmp($a, $b)} keys(%{$dh->{'sync-groups'}})){
     return $sync if (grep { /$instance/ } @{$dh->{'sync-groups'}->{$sync}->{monitor}});
   }
   return;
}

sub check_intf {
  my ($hash, $intf, $vrid) = @_;
  if ($intf) {
    if (!exists($hash->{instances}->{$intf})){
      print "VRRP is not running on $intf\n";
      return 1;
    }
    if ($vrid){
      if (!exists($hash->{instances}->{$intf}->{$vrid})){
        print "No VRRP group $vrid exists on $intf\n";
        return 1;
      }
    }
  }
  return;
}


sub print_detail {
  my ($dh,$intf,$group) = @_;
  print "--------------------------------------------------\n";
  foreach my $interface (sort {versioncmp($a, $b)} keys(%{$dh->{instances}})) {
    next if ($intf && $interface ne $intf);
    printf "Interface: %s\n", $interface;
    printf "--------------\n";
    foreach my $vrid (sort {versioncmp($a, $b)} keys(%{$dh->{instances}->{$interface}})){
      next if ($group && $vrid ne $group);
      printf "  Group: %s\n", $vrid;
      printf "  ----------\n";
      printf "  State:\t\t\t%s\n", 
        $dh->{instances}->{$interface}->{$vrid}->{state};
      printf "  Last transition:\t\t%s\n", 
        elapse_time($dh->{instances}->{$interface}->{$vrid}->{'last-transition'}, time);
      printf "\n";
      if ( $dh->{instances}->{$interface}->{$vrid}->{state} eq 'BACKUP') {
        printf "  Master router:\t\t%s\n", 
          $dh->{instances}->{$interface}->{$vrid}->{'master-router'};
        printf "  Master priority:\t\t%s\n",
          $dh->{instances}->{$interface}->{$vrid}->{'master-priority'};
        printf "\n";
      }
      my $version = $dh->{instances}->{$interface}->{$vrid}->{'vrrp-version'};
      printf "  Version:\t\t\t%s\n", $version;
      if ($dh->{instances}->{$interface}->{$vrid}->{'transmitting-device'} ne
          $dh->{instances}->{$interface}->{$vrid}->{'listening-device'}){ 
        printf "  RFC Compliant\n";
        printf "  Virtual MAC interface:\t%s\n",
          $dh->{instances}->{$interface}->{$vrid}->{'transmitting-device'};
        printf "  Address Owner:\t\t%s\n", 
          $dh->{instances}->{$interface}->{$vrid}->{'address-owner'};
        printf "\n";
        printf "  Source Address:\t\t%s\n",
          $dh->{instances}->{$interface}->{$vrid}->{'using-src_ip'};
      }
      printf "  Configured Priority:\t\t%s\n",
        $dh->{instances}->{$interface}->{$vrid}->{'base-priority'};
      printf "  Effective Priority:\t\t%s\n",
        $dh->{instances}->{$interface}->{$vrid}->{'effective-priority'};
      printf "  Advertisement interval:\t%s\n",
        $dh->{instances}->{$interface}->{$vrid}->{'advert-interval'};
      if ($version ne '3' ) {
        printf "  Authentication type:\t\t%s\n",
          $dh->{instances}->{$interface}->{$vrid}->{'authentication-type'};
      }
      printf "  Preempt:\t\t\t%s\n",
        $dh->{instances}->{$interface}->{$vrid}->{'preempt'};
      my $preempt_delay = $dh->{instances}->{$interface}->{$vrid}->{'preempt-delay'};
      if ($preempt_delay) {
        printf "  Preempt delay:\t\t\t%s\n",
          $preempt_delay;
      }
      my $start_delay = $dh->{instances}->{$interface}->{$vrid}->{'start-delay'};
      if ($start_delay) {
        printf "  Start delay:\t\t\t%s\n",
          $start_delay;
      }
      if ($version eq '3' ) {
        printf "  Accept:\t\t\t%s\n",
        $dh->{instances}->{$interface}->{$vrid}->{'accept'};
      }
      printf "\n";
      my $sync = find_sync($interface, $vrid, $dh);
      if ($sync) {
        printf "  Sync-group:\t\t\t%s\n", $sync;
        printf "\n";
      }
      my $track_interfaces =
          $dh->{instances}->{$interface}->{$vrid}->{'tracked-interfaces'};
      if ( $track_interfaces ) {
          printf "  Tracked Interfaces count:\t%s\n", $track_interfaces;

            foreach my $ifp (
                keys( %{ $dh->{instances}->{$interface}->{$vrid}->{ifps} } ) )
            {
                printf "    %s ", $ifp;
                printf "  state %s",
                  $dh->{instances}->{$interface}->{$vrid}->{'ifps'}->{$ifp}
                  ->{'state'};
                my $weight = $dh->{instances}->{$interface}->{$vrid}->{'ifps'}
                               ->{$ifp}->{'weight'};
                if ( defined $weight ) {
                    printf "      weight %s", $weight;
                }
                printf "\n";
            }
      }
      my $track_pathmon =
          $dh->{instances}->{$interface}->{$vrid}->{'tracked-path-monitors'};
      if ( $track_pathmon ) {
          printf "  Tracked Path Monitor count:\t%s\n", $track_pathmon;

            foreach my $monitor (
                keys( %{ $dh->{instances}->{$interface}->{$vrid}->{pms} } ) )
            {
                printf "    %s\n", $monitor;
                foreach my $policy (
                    keys( %{ $dh->{instances}->{$interface}->{$vrid}->{pms}->{$monitor} } ) )
                {
                    printf "      %s", $policy;
                    printf "  %s",
                      $dh->{instances}->{$interface}->{$vrid}->{pms}->{$monitor}->{$policy}
                      ->{'state'};
                    my $weight = $dh->{instances}->{$interface}->{$vrid}->{pms}
                                   ->{$monitor}->{$policy}->{'weight'};
                    if ( defined $weight ) {
                        printf "  weight %s", $weight;
                }
                printf "\n";
                }
            }
      }
      printf "  VIP count:\t\t\t%s\n",
        $dh->{instances}->{$interface}->{$vrid}->{'virtual-ip'};
      foreach my $vip (@{$dh->{instances}->{$interface}->{$vrid}->{vips}}){
         printf "    %s\n", $vip;
      }
      printf "\n";
    }
  }
}

sub print_summary {
  my ($dh, $intf, $group) = @_;
  my $format = "%-18s%-7s%-8s%-11s%-7s%-12s%s\n";
  printf $format, '','','','RFC','Addr','Last','Sync';
  printf $format, 'Interface','Group','State','Compliant','Owner','Transition','Group';
  printf $format, '---------','-----','-----','---------','-----','----------','-----';
  foreach my $interface (sort {versioncmp($a, $b)} keys(%{$dh->{instances}})) {
    next if ($intf && $interface ne $intf);
    foreach my $vrid (sort {versioncmp($a, $b)} keys(%{$dh->{instances}->{$interface}})){
      next if ($group && $vrid ne $group);
      my $state = $dh->{instances}->{$interface}->{$vrid}->{state};
      my $compliant = 
         ($dh->{instances}->{$interface}->{$vrid}->{'transmitting-device'} ne
          $dh->{instances}->{$interface}->{$vrid}->{'listening-device'}) ? 
        $dh->{instances}->{$interface}->{$vrid}->{'transmitting-device'} : 'no';
      my $addr_owner = ($dh->{instances}->{$interface}->{$vrid}->{'address-owner'});
      my $lt = elapse_time($dh->{instances}->{$interface}->{$vrid}->{'last-transition'}, time);
      my $sync = find_sync($interface, $vrid, $dh);
      $sync = "<none>" if (!defined($sync));
      printf $format, $interface, $vrid, $state, $compliant, $addr_owner, $lt, $sync;
    }
  }
  printf "\n";
}

sub print_interfaces {
  my ($dh, $intf, $group) = @_;
  foreach my $interface (sort {versioncmp($a, $b)} keys(%{$dh->{instances}})) {
    next if ($intf && $interface ne $intf);
    foreach my $vrid (sort {versioncmp($a, $b)} keys(%{$dh->{instances}->{$interface}})){
      next if ($group && $vrid ne $group);
      printf "$interface\n";
    }
  }
  printf "\n";
}

sub process_stats {
  my ($sh) = @_;
  my ($instance, $interface, $section);
  if ($dbus_object){ 
	$dbus_object->PrintStats();
  } else {
	kill 'SIGUSR2', get_pid();
  }		  
  wait_for_data($STATSFILE);
  open my $STATS, '<', $STATSFILE;
  while (<$STATS>)
  {
    m/VRRP Instance: vyatta-(.*?)-(.*)/ && do {
      $interface = $1;
      $instance = $2;
      $sh->{'instances'}->{$interface}->{$instance} = {};
      next;
    };
    m/Released master: (.*)/ && do {
      $sh->{'instances'}->{$interface}->{$instance}->{'released-master'} = $1;
      next;
    };
    m/Became master: (.*)/ && do {
      $sh->{'instances'}->{$interface}->{$instance}->{'became-master'} = $1;
      next;
    };
    m/(.*?):$/ && do {
      $section = conv_name $1;
      $sh->{'instances'}->{$interface}->{$instance}->{$section} = {};
      next;
    };
    m/(.*?): (.*)/ && do {
      my $id = conv_name $1;
      $sh->{'instances'}->{$interface}->{$instance}->{$section}->{$id} = $2;
      next;
    }; 
    print $_;
  }
 
  close $STATS;
}

sub print_stats {
  my ($sh, $intf, $group) = @_;
  print "--------------------------------------------------\n";
  foreach my $interface (sort {versioncmp($a, $b)} keys(%{$sh->{instances}})) {
    next if ($intf && $interface ne $intf);
    printf "Interface: %s\n", $interface;
    printf "--------------\n";
    foreach my $vrid (sort {versioncmp($a, $b)} keys(%{$sh->{instances}->{$interface}})){
      next if ($group && $vrid ne $group);
      printf "  Group: %s\n", $vrid;
      printf "  ----------\n";
      printf "  Advertisements:\n";
      printf "    Received:\t\t\t%d\n", 
        $sh->{instances}->{$interface}->{$vrid}->{advertisements}->{received};
      printf "    Sent:\t\t\t%d\n",
        $sh->{instances}->{$interface}->{$vrid}->{advertisements}->{sent};
      printf "\n";
      printf "  Became master:\t\t%d\n",
        $sh->{instances}->{$interface}->{$vrid}->{'became-master'};
      printf "  Released master:\t\t%d\n",
        $sh->{instances}->{$interface}->{$vrid}->{'released-master'};
      printf "\n";
      printf "  Packet errors:\n";
      printf "    Length:\t\t\t%d\n", 
        $sh->{instances}->{$interface}->{$vrid}->{'packet-errors'}->{length};
      printf "    TTL:\t\t\t%d\n", 
        $sh->{instances}->{$interface}->{$vrid}->{'packet-errors'}->{ttl};
      printf "    Invalid type:\t\t%d\n", 
        $sh->{instances}->{$interface}->{$vrid}->{'packet-errors'}->{'invalid-type'};
      printf "    Advertisement interval:\t%d\n", 
        $sh->{instances}->{$interface}->{$vrid}->{'packet-errors'}->{'advertisement-interval'};
      printf "    Address List:\t\t%d\n", 
        $sh->{instances}->{$interface}->{$vrid}->{'packet-errors'}->{'address-list'};
      printf "\n";
      printf "  Authentication Errors:\n";
      printf "    Invalid type:\t\t%d\n",
        $sh->{instances}->{$interface}->{$vrid}->{'authentication-errors'}->{'invalid-type'};
      printf "    Type mismatch:\t\t%d\n",
        $sh->{instances}->{$interface}->{$vrid}->{'authentication-errors'}->{'type-mismatch'};
      printf "    Failure:\t\t\t%d\n",
        $sh->{instances}->{$interface}->{$vrid}->{'authentication-errors'}->{'failure'};
      printf "\n";
      printf "  Priority Zero Advertisements:\n";
      printf "    Received\t\t\t%d\n",
        $sh->{instances}->{$interface}->{$vrid}->{'priority-zero'}->{'received'};
      printf "    Sent\t\t\t%d\n",
        $sh->{instances}->{$interface}->{$vrid}->{'priority-zero'}->{'sent'};
      printf "\n";
    }
  }
}

sub print_sync {
  my ($dh, $sync_group) = @_;
  print "--------------------------------------------------\n";
  foreach my $sync (sort {versioncmp($a, $b)} keys(%{$dh->{'sync-groups'}})){
    next if ($sync_group && $sync ne $sync_group);
    printf "Group: %s\n", $sync; 
    printf "---------\n"; 
    printf "  State: %s\n", $dh->{'sync-groups'}->{$sync}->{state};
    printf "  Monitoring:\n";
    foreach my $mon (sort {versioncmp($a, $b)} @{$dh->{'sync-groups'}->{$sync}->{monitor}}){
      my ($intf, $vrid) = $mon =~ m/vyatta-(.*?)-(.*)/;
      printf "    Interface: %s, Group: %s\n", $intf, $vrid;
    }
    printf "\n";
  }
}

# Given a vrrp group number, find the interface that group number is configured on.
# If the group number is not unique across the system, this function will simply
# return the first interface it comes across with that group number configured.
sub get_associated_intf {
  my ($vrrp_group) = @_;

  my $hash = {};

  process_data $hash;

  if(not defined $vrrp_group) {
    return;
  }

  foreach my $interface (sort {versioncmp($a, $b)} keys(%{$hash->{instances}})) {
    foreach my $vrid (sort {versioncmp($a, $b)} keys(%{$hash->{instances}->{$interface}})) {
      if ($vrrp_group == $vrid) {
       return $interface;
      }
    }
  }
  # Reaching here means we've been unable to find an associated interface.
  return;
}

sub get_state {
  my ($intf, $vrrp_group) = @_;

  my $hash = {};

  if( (not defined $intf) or (not defined $vrrp_group) ) {
      return;
  }

  process_data $hash;

  return $hash->{instances}->{$intf}->{$vrrp_group}->{state};
}

1;
