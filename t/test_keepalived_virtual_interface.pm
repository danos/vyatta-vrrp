#! /usr/bin/perl

use strict;
use warnings;

package test_keepalived_virtual_interface;
use base qw(Test::Class);
use Test::More;

use File::Basename;
use Cwd 'abs_path';
use lib abs_path(dirname(__FILE__) . "/../lib");
use Vyatta::VRRP::virtual_interface;

my $data_path = Cwd::getcwd();
my $base_name = basename($data_path);

if ( ($base_name eq "vyatta-vrrp") or ($base_name eq "BUILD") ) {
    $data_path .= "/t/data/";
} elsif ($base_name eq "t") {
    $data_path .= "/data/";
}

sub set_up : Test(setup) {
    my $self = shift;
    @{ $self->{file_list} } = ($data_path."test_simple_block.txt",
    $data_path."test_no_virtuals.conf",
    $data_path."test_keepalived_simple.conf",
    $data_path."test_keepalived_complex.conf");
}

sub tear_down : Test(teardown) {
    my $self = shift;
}

sub _test_load_module : Test {
    require_ok("Vyatta::VRRP::virtual_interface");
}

sub test_simple_block_get_virtual_interfaces : Test {
    my $self = shift;
    my @file_list = @{ $self->{file_list} };
    my $conf_file = $file_list[0];
    my %expected = ("vyatta-dp0s3-1", "dp0vrrp1");
    my %got = get_virtual_interfaces($conf_file);
    is_deeply(\%got, \%expected, "Test simple block get_virtual_interfaces");
}

sub test_simple_block_get_largest_virtual_interface : Test {
    my $self = shift;
    my @file_list = @{ $self->{file_list} };
    my $conf_file = $file_list[0];
    my $expected = "dp0vrrp1";
    my %virt_intf_mapping = get_virtual_interfaces($conf_file);
    my $got = get_largest_virtual_interface(%virt_intf_mapping);
    is($got, $expected, "Test simple block get_largest_virtual_interface");
}

sub test_simple_block_increment_virtual_interface : Test {
    my $self = shift;
    my @file_list = @{ $self->{file_list} };
    my $conf_file = $file_list[0];
    my $expected = "dp0vrrp2";
    my %virt_intf_mapping = get_virtual_interfaces($conf_file);
    my $largest_virt_intf = get_largest_virtual_interface(%virt_intf_mapping);
    my $got = increment_virtual_interface($largest_virt_intf);
    is($got, $expected, "Test simple block increment_virtual_interface");
}

sub test_no_vmacs_get_virtual_interfaces : Test {
    my $self = shift;
    my @file_list = @{ $self->{file_list} };
    my $conf_file = $file_list[1];
    my %expected = ();
    my %got = get_virtual_interfaces($conf_file);
    is_deeply(\%got, \%expected, "Test no vmacs get_virtual_interfaces");
}

sub test_no_vmacs_get_largest_virtual_interface : Test {
    my $self = shift;
    my @file_list = @{ $self->{file_list} };
    my $conf_file = $file_list[1];
    my $expected = "";
    my %virt_intf_mapping = get_virtual_interfaces($conf_file);
    my $got = get_largest_virtual_interface(%virt_intf_mapping);
    is($got, $expected, "Test no vmacs get_largest_virtual_interface");
}

sub test_no_vmacs_increment_virtual_interface : Test {
    my $self = shift;
    my @file_list = @{ $self->{file_list} };
    my $conf_file = $file_list[1];
    my $expected = "";
    my %virt_intf_mapping = get_virtual_interfaces($conf_file);
    my $largest_virt_intf = get_largest_virtual_interface(%virt_intf_mapping);
    my $got = increment_virtual_interface($largest_virt_intf);
    is($got, $expected, "Test no vmacs increment_virtual_interface");
}

sub test_simple_file_get_virtual_interfaces : Test {
    my $self = shift;
    my @file_list = @{ $self->{file_list} };
    my $conf_file = $file_list[2];
    my %expected = ("vyatta-dp0s3-1", "dp0vrrp1", "vyatta-dp0s3-2", "dp0vrrp2",
    "vyatta-dp0s6-1", "dp0vrrp3");
    my %got = get_virtual_interfaces($conf_file);
    is_deeply(\%got, \%expected, "Test simple file get_virtual_interfaces");
}

sub test_simple_file_get_largest_virtual_interface : Test {
    my $self = shift;
    my @file_list = @{ $self->{file_list} };
    my $conf_file = $file_list[2];
    my $expected = "dp0vrrp3";
    my %virt_intf_mapping = get_virtual_interfaces($conf_file);
    my $got = get_largest_virtual_interface(%virt_intf_mapping);
    is($got, $expected, "Test simple file get_largest_virtual_interface");
}

sub test_simple_file_increment_virtual_interface : Test {
    my $self = shift;
    my @file_list = @{ $self->{file_list} };
    my $conf_file = $file_list[2];
    my $expected = "dp0vrrp4";
    my %virt_intf_mapping = get_virtual_interfaces($conf_file);
    my $largest_virt_intf = get_largest_virtual_interface(%virt_intf_mapping);
    my $got = increment_virtual_interface($largest_virt_intf);
    is($got, $expected, "Test simple file increment_virtual_interface");
}

sub test_complex_file_get_virtual_interfaces : Test {
    my $self = shift;
    my @file_list = @{ $self->{file_list} };
    my $conf_file = $file_list[3];
    my %expected = ("vyatta-dp0s3-1", "dp0vrrp1", "vyatta-dp0s3-2", "dp0vrrp2",
    "vyatta-dp0s6-1", "dp0vrrp3", "vyatta-dp0s6-2", "dp0vrrp16", "vyatta-dp0s6-3",
    "dp0vrrp4");
    my %got = get_virtual_interfaces($conf_file);
    is_deeply(\%got, \%expected, "Test complex file get_virtual_interfaces");
}

sub test_complex_file_get_largest_virtual_interface : Test {
    my $self = shift;
    my @file_list = @{ $self->{file_list} };
    my $conf_file = $file_list[3];
    my $expected = "dp0vrrp16";
    my %virt_intf_mapping = get_virtual_interfaces($conf_file);
    my $got = get_largest_virtual_interface(%virt_intf_mapping);
    is($got, $expected, "Test complex file get_largest_virtual_interface");
}

sub test_complex_file_increment_virtual_interface : Test {
    my $self = shift;
    my @file_list = @{ $self->{file_list} };
    my $conf_file = $file_list[3];
    my $expected = "dp0vrrp17";
    my %virt_intf_mapping = get_virtual_interfaces($conf_file);
    my $largest_virt_intf = get_largest_virtual_interface(%virt_intf_mapping);
    my $got = increment_virtual_interface($largest_virt_intf);
    is($got, $expected, "Test complex file increment_virtual_interface");
}


1;

