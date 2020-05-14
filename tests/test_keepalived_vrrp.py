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

    @pytest.mark.sanity
    @pytest.mark.parametrize(
        "keepalived_config,yang,rfc_num,intf",
        [(pytest.lazy_fixture("dataplane_group_keepalived_config"),
         pytest.lazy_fixture("generic_group"), -1, "dp0p1s1"),
         (pytest.lazy_fixture("max_group_keepalived_config"),
         pytest.lazy_fixture("max_config_group"), 1, "dp0p1s1"),
         (pytest.lazy_fixture("generic_v3_group_keepalived_config"),
         pytest.lazy_fixture("generic_v3_group"), -1, "dp0p1s1"),
         (pytest.lazy_fixture("generic_ipv6_group_keepalived_config"),
         pytest.lazy_fixture("generic_ipv6_group"), -1, "dp0p1s1"),
         (pytest.lazy_fixture("pathmon_track_group_keepalived_config"),
         pytest.lazy_fixture("pathmon_track_group"), -1, "dp0p1s1"),
         (pytest.lazy_fixture("legacy_track_group_keepalived_config"),
         pytest.lazy_fixture("legacy_track_group"), -1, "dp0p1s1"),
         (pytest.lazy_fixture(
             "legacy_and_enhanced_track_group_keepalived_config"),
         pytest.lazy_fixture("legacy_and_enhanced_track_group"), -1,
            "dp0p1s1"),
         (pytest.lazy_fixture(
             "legacy_and_pathmon_enhanced_track_group_keepalived_config"),
         pytest.lazy_fixture("legacy_and_pathmon_enhanced_track_group"), -1,
            "dp0p1s1"),
         (pytest.lazy_fixture("accept_v3_group_keepalived_config"),
         pytest.lazy_fixture("accept_v3_group"), -1, "dp0p1s1"),
         (pytest.lazy_fixture("nopreempt_v3_group_keepalived_config"),
         pytest.lazy_fixture("nopreempt_v3_group"), -1, "dp0p1s1"),
         (pytest.lazy_fixture("ah_auth_v3_group_keepalived_config"),
         pytest.lazy_fixture("ah_auth_v3_group"), -1, "dp0p1s1"),
         (pytest.lazy_fixture("runtransition_v3_group_keepalived_config"),
         pytest.lazy_fixture("runtransition_v3_group"), -1, "dp0p1s1"),
         (pytest.lazy_fixture("switch_rfc_group_keepalived_config"),
         pytest.lazy_fixture("generic_rfc_group"), 1, "sw0.10"),
         (pytest.lazy_fixture(
             "generic_v3_fast_advert_group_keepalived_config"
            ),
         pytest.lazy_fixture("generic_v3_fast_advert_group"), -1, "dp0p1s1")],
        ids=["Simple", "Complex", "VRRPv3", "IPv6 group",
             "Pathmon tracking",
             "Legacy tracking", "Legacy & Enhanced Tracking",
             "Legacy Interface & Enhanced Pathmon Tracking", "Accept VRRPv3",
             "No Preempt VRRPv3", "AH Auth VRRPv3",
             "Run transition scripts", "Switch interface",
             "VRRPv3 fast-advert"])
    def test_vrrp_group_config_string(
            self, keepalived_config, yang, rfc_num, intf):
        result = VrrpGroup(intf, "0", yang, rfc_num)
        assert keepalived_config == str(result)

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
