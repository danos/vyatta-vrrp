# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import pytest

from vyatta.vrrp_vci.keepalived.vrrp import VrrpGroup


class TestKeepalivedVrrpGroup:

    # pylint: disable=protected-access
    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=too-many-arguments
    def test_vrrp_group_instance_name(
            self, simple_vrrp_group_object):
        expected = "vyatta-dp0p1s1-1"
        assert simple_vrrp_group_object.instance_name == \
            expected

    @pytest.mark.parametrize(
        "expected,yang,rfc_num,intf",
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
             "generic_v3_fast_advert_group_keepalived_config"),
          pytest.lazy_fixture("generic_v3_fast_advert_group"), -1, "dp0p1s1"),
         (pytest.lazy_fixture(
             "generic_v3_fast_advert_group_seconds_keepalived_config"),
          pytest.lazy_fixture("generic_v3_fast_advert_seconds_group"), -1,
          "dp0p1s1"),
         (pytest.lazy_fixture(
             "generic_v3_fast_advert_group_between_seconds_keepalived_config"),
          pytest.lazy_fixture("generic_v3_fast_advert_between_seconds_group"),
          -1, "dp0p1s1"),
         (pytest.lazy_fixture("switch_max_group_keepalived_config"),
          pytest.lazy_fixture("switch_max_config_group"), 1, "sw0.10"),
         (pytest.lazy_fixture("bonding_max_group_keepalived_config"),
          pytest.lazy_fixture("bonding_max_config_group"), 1, "dp0bond0"),
         (pytest.lazy_fixture("route_to_track_group_keepalived_config"),
          pytest.lazy_fixture("route_to_track_group"), 1, "dp0p1s1")],
        ids=["Simple", "Complex", "VRRPv3", "IPv6 group",
             "Pathmon tracking",
             "Legacy tracking", "Legacy & Enhanced Tracking",
             "Legacy Interface & Enhanced Pathmon Tracking", "Accept VRRPv3",
             "No Preempt VRRPv3", "AH Auth VRRPv3",
             "Run transition scripts", "Switch interface",
             "VRRPv3 fast-advert subsecond",
             "VRRPv3 fast-advert second boundary",
             "VRRPv3 fast-advert between full seconds",
             "Complex switch config",
             "Complex bonding config",
             "Route to tracking"])
    def test_vrrp_group_config_string(
            self, expected, yang, rfc_num, intf):
        assert str(VrrpGroup(intf, "0", yang, rfc_num)) == expected

    def test_vrrp_group_preempt_delay_printed_warnings(
            self, preempt_delay_ignored_group, caplog):
        VrrpGroup("dp0p1s1", "0", preempt_delay_ignored_group)
        assert "preempt delay is ignored when preempt=false" in caplog.text

    def test_vrrp_group_rfc_name_length_printed_warnings(
            self, generic_group, caplog):
        generic_group["rfc-compatibility"] = [None]
        VrrpGroup("dp0p1s1", "0", generic_group, 1234567890)
        assert "generated interface name is longer than 15 characters" in \
            caplog.text
