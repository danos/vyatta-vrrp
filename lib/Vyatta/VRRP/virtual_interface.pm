#! /usr/bin/perl
#
# Copyright (c) 2019 AT&T Intellectual Property.
# All rights reserved.
#
# Copyright (c) 2014 by Brocade Communications Systems, Inc.
# All rights reserved.
# 
# SPDX-License-Identifier: GPL-2.0-only
#

use strict;
use warnings;
use Sort::Versions;

our @EXPORT = qw(get_virtual_interfaces);
use base qw(Exporter);

# Description:
#   Open the file passed to the subroutine and return a hash of all the vmacs
#   each VRRP group instance uses.
# Input:
#   conf_file   -   Path to the file we are to read.
# Output
#   output      -   Hash containg the mapping between the unique interface and
#                   the vmac used for the instance. Will only return a mapping
#                   for which a virtual interface is needed.
sub get_virtual_interfaces {
    my $conf_file = shift;
    my %output = ();
    open(my $FH, "<", $conf_file) or return %output;
    my $key;
    my $value;
    my $brace = 0;
    while (my $line = <$FH>) {
        chomp $line;
        if ($line =~ m/vrrp_instance\s+(.*)\s+/) {
            $key = $1;
            $brace++;
        } elsif ($line =~ m/use_vmac\s+(.*)/) {
            $value = $1;
        } elsif ($line =~ m/{/) {
            $brace++;
        } elsif ($line =~ m/}/) {
            $brace--;
        }
        if (defined $key and defined $value) {
            $output{$key} = $value;
        }
        if ($brace == 0) {
            undef $value;
            undef $key;
        }

    }
    close($FH);
    return %output;
}

# Description:
#   Sort a list of virtual interface names and return the "largest" interface.
#   Largest here is defined by the name that contains the largest number at the
#   end of the string.
# Input:
#   mapping         -   A hash containing the mapping between instance names and
#                       virtual interface names.
# Output
#   largest name    -   The return value can be one of two things. An empty
#                       string if the value array is empty; or the last entry in
#                       the array (which should be the largest name).
sub get_largest_virtual_interface {
    my %mapping = @_;
    my @hash_keys = keys %mapping;
    my @hash_values = values %mapping;

    #We wish to sort Naturally the sort included by defaut in Perl will sort
    #lexicographically, so dp0vrrp16 would come before dp0vrrp4. This isn't what
    #we want. Using Sort::Version does the comparison well enough for our needs.
    my @sorted_values = sort {versioncmp($a, $b)} @hash_values;
    if (scalar @sorted_values) {
        return $sorted_values[-1];
    } else {
        return "";
    }
}

# Description:
#   Create a new interface name by incrementing the number of the name passed to
#   the routine.
# Input:
#   virt_intf   -   String containing an interface name.
# Output
#   new_intf    -   New interface name created by adding one to $virt_intf
sub increment_virtual_interface {
    my $virt_intf = shift;
    if ($virt_intf eq "") {
        return $virt_intf;
    }
    $virt_intf =~ m/(.*vrrp)(\d+)/;
    my $intf = $1;
    my $vrrp_num = ($2)+1;
    my $new_intf = $intf.$vrrp_num;
    return $new_intf;
}



1;
