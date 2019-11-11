#! /usr/bin/perl

use strict;
use warnings 'all';
BEGIN { push @INC, "t/" };
use test_keepalived_virtual_interface;

Test::Class->runtests();
