#! /usr/bin/python3

# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import pytest
from vyatta.keepalived.vrrp import VrrpGroup


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

    @pytest.mark.parametrize(
        "expected,result",
        [(pytest.lazy_fixture("dataplane_group_keepalived_config"),
         pytest.lazy_fixture("simple_vrrp_group_object")),
         (pytest.lazy_fixture("max_group_keepalived_config"),
         pytest.lazy_fixture("fuller_vrrp_group_object")),
         (pytest.lazy_fixture("generic_v3_group_keepalived_config"),
         pytest.lazy_fixture("simple_v3_vrrp_group_object")),
         (pytest.lazy_fixture("pathmon_track_group_keepalived_config"),
         pytest.lazy_fixture("pathmon_track_vrrp_group_object")),
         (pytest.lazy_fixture("legacy_track_group_keepalived_config"),
         pytest.lazy_fixture("legacy_track_vrrp_group_object"))],
        ids=["Simple", "Complex", "VRRPv3", "Pathmon tracking",
             "Legacy tracking"])
    def test_vrrp_group_config_string(
            self, expected, result):
        assert expected == str(result)

    def test_vrrp_group_preempt_delay_printed_warnings(
            self, preempt_delay_ignored_group, capsys):
        VrrpGroup("dp0p1s1", "0", preempt_delay_ignored_group)
        print_result = \
            "Warning: preempt delay is ignored when preempt=false\n\n"
        captured = capsys.readouterr()
        assert print_result == captured.out

    def test_vrrp_group_rfc_name_length_printed_warnings(
            self, generic_group, capsys):
        generic_group["rfc-compatibility"] = [None]
        VrrpGroup("dp0p1s1", "0", generic_group, 1234567890)
        print_result = \
            "Warning: generated interface name is longer than 15 " + \
            "characters\n\n"
        captured = capsys.readouterr()
        assert print_result == captured.out
