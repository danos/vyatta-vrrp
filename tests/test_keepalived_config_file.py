# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import json
from pathlib import Path

import pytest

import vyatta.vrrp_vci.keepalived.util as util


class TestKeepalivedConfigFile:

    # pylint: disable=protected-access
    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=too-many-arguments

    @pytest.mark.parametrize(
        "keepalived,expected_path",
        [
            (pytest.lazy_fixture("keepalived_config"),
             "/etc/keepalived/keepalived.conf"),
            (pytest.lazy_fixture("non_default_keepalived_config"),
             "/test/file/path.conf"),
        ],
        ids=[
            "Default path file",
            "Nondefault path file"
        ]
    )
    def test_config_path_default(self, keepalived, expected_path):
        assert keepalived.config_file_path() == expected_path

    def test_implementation_name(self, keepalived_config):
        expected = "Keepalived"
        assert keepalived_config.impl_name() == expected

    @pytest.mark.parametrize(
        "config_lines,expected_yang,keepalived",
        [
            ([[]], {}, pytest.lazy_fixture("keepalived_config")),
            (
                pytest.lazy_fixture("complex_keepalived_config_block"),
                pytest.lazy_fixture("max_config_group"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture(
                    "pathmon_track_group_keepalived_config_block"
                ),
                pytest.lazy_fixture("pathmon_track_group"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture(
                    "route_to_track_group_keepalived_config_block"
                ),
                pytest.lazy_fixture("route_to_track_group"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture("simple_keepalived_config_block"),
                pytest.lazy_fixture("generic_group"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture(
                    "switch_rfc_group_keepalived_config_block"
                ),
                pytest.lazy_fixture("generic_rfc_group"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture(
                    "dataplane_vif_group_keepalived_config_block"
                ),
                pytest.lazy_fixture("modified_vif_group"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture("syncgroup_group_keepalived_config_block"),
                pytest.lazy_fixture("sync_group1"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture(
                    "v3_fast_advert_group_keepalived_config_block"
                ),
                pytest.lazy_fixture("generic_v3_fast_advert_group"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture(
                    "v3_fast_advert_group_seconds_keepalived_config_block"
                ),
                pytest.lazy_fixture("generic_v3_fast_advert_seconds_group"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture(
                    "v3_fast_advert_group_between_seconds_keepalived_"
                    "config_block"
                ),
                pytest.lazy_fixture(
                    "generic_v3_fast_advert_between_seconds_group"
                ),
                pytest.lazy_fixture("keepalived_config")
            ),
        ],
        ids=[
            "No config", "Convert max config",
            "Convert path monitor tracking config",
            "Convert route to tracking config",
            "Convert minimal config", "Convert switch RFC interface",
            "Convert dataplane VIF group",
            "Convert group with syncgroup",
            "Convert subsecond fast-advertise-interval group",
            "Convert second fast-advertise-interval group",
            "convert between two second fast-advertise-interval group"
        ]
    )
    def test_convert_keepalived_config_to_yang(
            self, config_lines, expected_yang, keepalived):
        assert keepalived._convert_keepalived_config_to_yang(config_lines[0]) \
            == expected_yang

    @pytest.mark.parametrize(
        "config_string,yang_config,keepalived",
        [
            (
                "", {},
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture("simple_keepalived_config"),
                pytest.lazy_fixture("simple_config"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture("generic_v3_keepalived_config"),
                pytest.lazy_fixture("generic_v3_config"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture("syncgroup_keepalived_config"),
                pytest.lazy_fixture("syncgroup_config"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture("multiple_syncgroup_keepalived_config"),
                pytest.lazy_fixture("multiple_syncgroup_config"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture("complex_keepalived_config"),
                pytest.lazy_fixture("complex_config"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture("bonding_keepalived_config"),
                pytest.lazy_fixture("bonding_config"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture("bonding_complex_keepalived_config"),
                pytest.lazy_fixture("bonding_complex_config"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture("parent_and_vif_keepalived_config"),
                pytest.lazy_fixture("parent_and_vif_config"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture("switch_keepalived_config"),
                pytest.lazy_fixture("switch_config"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture("switch_complex_keepalived_config"),
                pytest.lazy_fixture("switch_complex_config"),
                pytest.lazy_fixture("keepalived_config")
            ),
        ],
        ids=[
            "No config", "Minimal config", "v3 Config",
            "Sync group config", "Multiple sync groups",
            "Complex config",
            "Bonding config", "Bonding complex config",
            "Parent and vif config",
            "switch config", "Switch complex config",
        ]
    )
    def test_config_to_vci_format(
            self, config_string, yang_config, keepalived):
        expected = json.dumps(yang_config)
        assert keepalived.convert_to_vci_format(config_string) == expected

    def test_read_config_no_file(self, non_default_keepalived_config):
        with pytest.raises(FileNotFoundError):
            non_default_keepalived_config.read_config()

    def test_read_config_file_exists(self, tmp_file_keepalived_config):
        result = tmp_file_keepalived_config.read_config()
        assert result is not None

    def test_read_config_keepalived_config(
            self, tmp_file_keepalived_config,
            simple_keepalived_config):
        result = tmp_file_keepalived_config.read_config()
        assert result == simple_keepalived_config

    @pytest.mark.parametrize(
        "fakes,yang_config,expected,keepalived",
        [
            (
                None,
                {},
                [],
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                None,
                pytest.lazy_fixture("top_level_dictionary"),
                [],
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                None,
                pytest.lazy_fixture("no_vrrp_config"),
                [],
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                None,
                pytest.lazy_fixture("disabled_vrrp_config"),
                [],
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture("mock_pydbus"),
                pytest.lazy_fixture("simple_config"),
                pytest.lazy_fixture("simple_vrrp_group_object"),
                pytest.lazy_fixture("keepalived_config")
            ),
            (
                pytest.lazy_fixture("mock_pydbus"),
                pytest.lazy_fixture("complex_config"),
                pytest.lazy_fixture("fuller_vrrp_group_object"),
                pytest.lazy_fixture("keepalived_config")
            ),
        ],
        ids=[
            "No Config", "No Interface config", "No VRRP config",
            "Disabled VRRP group", "Simple VRRP config", "Complex config"
        ]
    )
    def test_update_config(
            self, fakes, yang_config, expected, keepalived):
        if not isinstance(expected, list):
            # Need to instansiate lazy fixtures
            expected = [expected]
        keepalived.update(yang_config)
        assert str(keepalived.vrrp_instances) == str(expected)

    def test_update_config_error_when_vif_under_intf(
            self, keepalived_config, simple_dataplane_vif_config):
        with pytest.raises(ValueError):
            keepalived_config.update(simple_dataplane_vif_config)

    def test_write_config_file_exist(
            self, tmp_path, tmp_file_keepalived_config_no_write):
        file_path = Path(f"{tmp_path}/keepalived.conf")
        result = False
        expected = file_path.exists()
        assert result == expected
        tmp_file_keepalived_config_no_write.write_config()
        result = True
        expected = file_path.exists()
        assert result == expected

    def test_shutdown(
            self, tmp_path, tmp_file_keepalived_config_no_write):
        file_path = Path(f"{tmp_path}/keepalived.conf")
        result = False
        expected = file_path.exists()
        assert result == expected
        tmp_file_keepalived_config_no_write.write_config()
        result = True
        expected = file_path.exists()
        assert result == expected
        tmp_file_keepalived_config_no_write.shutdown()
        result = False
        expected = file_path.exists()
        assert result == expected

    @pytest.mark.parametrize(
        "expected,config_block",
        [
            ({}, []),
            ({}, ["virtual_ipaddress {", "10.10.10.100/25", "}"]),
            (
                {
                    "authentication":
                        {"password": "test", "type": "plaintext-password"}
                },
                ["authentication {", "auth_type PASS", "auth_pass test", "}"]
            ),
            (
                {
                    "authentication":
                        {"password": "test", "type": "ah"}
                },
                ["authentication {", "auth_type AH", "auth_pass test", "}"]
            )
        ],
        ids=["No Config", "No Notify Config",
             "Plaintext Authentication Config Exists",
             "Authentication Header Config Exists"])
    def test_convert_authentication_config(
            self, keepalived_config, expected, config_block):
        result = {}
        keepalived_config._convert_authentication_config(
            config_block, result)
        assert result == expected

    @pytest.mark.parametrize(
        "expected,config_block",
        [
            ({}, []),
            ({}, ["virtual_ipaddress {", "10.10.10.100/25", "}"]),
            (
                {"notify": {"bgp": [None], "ipsec": [None]}},
                [
                    "notify {",
                    "/opt/vyatta/sbin/vyatta-ipsec-notify.sh",
                    "/opt/vyatta/sbin/notify-bgp",
                    "}"
                ]
            )
        ],
        ids=["No Config", "No Notify Config", "Notify Config Exists"])
    def test_convert_notify_proto_config(
            self, keepalived_config, expected, config_block):
        result = {}
        keepalived_config._convert_notify_proto_config(
            config_block, result)
        assert result == expected

    @pytest.mark.parametrize(
        "expected,config_block,result",
        [
            ({"track": {"interface": [{"name": "lo1"}, {"name": "dp0p2",
                                                        "weight":
                                                        {"type": "decrement",
                                                         "value": 10}}]}},
             ["track {", "interface {", "lo1", "dp0p2 weight -10", "}"],
             {"track": {}}),
            ({}, ["virtual_ipaddress {", "10.10.10.100/25", "}"], {})
        ],
        ids=["Config exists", "Config doesn't exist"])
    def test_convert_interface_tracking_config(self, expected, config_block,
                                               keepalived_config, result):
        keepalived_config._convert_interface_tracking_config(
            config_block, result, 0)
        assert result == expected

    @pytest.mark.parametrize(
        "expected,config_block,result",
        [
            ({
                "track":
                {
                    "vyatta-vrrp-path-monitor" +
                    "-track-interfaces-dataplane-v1:" +
                    "path-monitor": {
                        "monitor": [
                            {
                                "name": "test_monitor",
                                "policy": [
                                    {
                                        "name": "test_policy"
                                    }
                                ]
                            }
                        ]
                    }
                }
            },
                ["track {", "pathmon {",
                 "monitor test_monitor policy test_policy", "}"],
                {"track": {}}
            ),
            ({}, ["virtual_ipaddress {", "10.10.10.100/25", "}"], {})
        ],
        ids=["Config exists", "Config doesn't exist"])
    def test_convert_pathmon_tracking_config(self, expected, config_block,
                                             keepalived_config, result):
        keepalived_config._convert_pathmon_tracking_config(
            config_block, result, 0, util.intf_type.dataplane)
        assert result == expected

    @pytest.mark.parametrize(
        "expected,config_block,result",
        [
            ({
                "track":
                {
                    "vyatta-vrrp-route-to" +
                    "-track-interfaces-dataplane-v1:" +
                    "route-to": [{
                        "route": "10.10.10.0/24",
                    }]
                }
            },
                ["track {", "route_to {",
                 "10.10.10.0/24", "}"],
                {"track": {}}
            ),
            ({}, ["virtual_ipaddress {", "10.10.10.100/25", "}"], {})
        ],
        ids=["Config exists", "Config doesn't exist"])
    def test_convert_route_to_config(self, expected, config_block,
                                     keepalived_config, result):
        keepalived_config._convert_route_to_tracking_config(
            config_block, result, 0, util.intf_type.dataplane)
        assert result == expected
