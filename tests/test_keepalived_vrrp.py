#! /usr/bin/python3

# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import pytest


class TestKeepalivedVrrpGroup:

    # pylint: disable=protected-access
    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=too-many-arguments
    def test_vrrp_group_instance_name(
            self, simple_vrrp_group_object):
        expected = "vyatta-dp0p1s1-1"
        result = simple_vrrp_group_object.instance_name
        assert result == expected

    def test_vrrp_group_config_string(
            self, simple_vrrp_group_object,
            dataplane_group_keepalived_config):
        simple_vrrp_group_object._priority = 100
        expected = dataplane_group_keepalived_config
        result = str(simple_vrrp_group_object)
        assert result == expected
