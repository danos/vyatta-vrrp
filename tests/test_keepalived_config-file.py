#! /usr/bin/python3

# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import copy
import json
from pathlib import Path
import vyatta.keepalived.util as util
import pytest


class TestKeepalivedConfigFile:

    # pylint: disable=protected-access
    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=too-many-arguments
    def test_config_path_default(self, keepalived_config):
        expected = "/etc/keepalived/keepalived.conf"
        result = keepalived_config.config_file_path()
        assert result == expected

    def test_config_path_user_defined(self, non_default_keepalived_config):
        expected = "/test/file/path.conf"
        result = non_default_keepalived_config.config_file_path()
        assert result == expected

    def test_implementation_name(self, keepalived_config):
        expected = "Keepalived"
        result = keepalived_config.impl_name()
        assert result == expected

    def test_convert_no_vrrp_keepalived_conf_to_yang(
            self, keepalived_config):
        expected = {}
        result = keepalived_config._convert_keepalived_config_to_yang([])
        assert expected == result

    def test_convert_fuller_vrrp_keepalived_conf_to_yang(
            self, max_group_keepalived_config, max_config_group,
            keepalived_config):
        expected = max_config_group
        config_split = max_group_keepalived_config.splitlines()
        indexes = util.get_config_indexes(
            config_split, "vrrp_instance")
        config_block = util.get_config_blocks(
            config_split, indexes)[0]
        result = keepalived_config._convert_keepalived_config_to_yang(
            config_block)
        assert expected == result

    def test_convert_minimal_vrrp_keepalived_conf_to_yang(
            self, dataplane_group_keepalived_config, generic_group,
            keepalived_config):
        expected = generic_group
        config_split = dataplane_group_keepalived_config.splitlines()
        indexes = util.get_config_indexes(
            config_split, "vrrp_instance")
        config_block = util.get_config_blocks(
            config_split, indexes)[0]
        result = keepalived_config._convert_keepalived_config_to_yang(
            config_block)
        assert expected == result

    def test_convert_vif_vrrp_keepalived_conf_to_yang(
            self, dataplane_vif_group_keepalived_config, generic_group,
            keepalived_config):
        expected = generic_group
        expected["virtual-address"] = ["10.10.2.100/25"]
        expected["priority"] = 100
        expected["tagnode"] = 2
        config_split = dataplane_vif_group_keepalived_config.splitlines()
        indexes = util.get_config_indexes(
            config_split, "vrrp_instance")
        config_block = util.get_config_blocks(
            config_split, indexes)[0]
        del expected["priority"]
        result = keepalived_config._convert_keepalived_config_to_yang(
            config_block)
        assert expected == result

    def test_config_to_vci_format_no_config(self, keepalived_config):
        result = json.dumps({})
        expect = keepalived_config.convert_to_vci_format("")
        assert result == expect

    def test_config_to_vci_format_minimal_config(
            self, autogeneration_string, dataplane_group_keepalived_config,
            keepalived_config, simple_config, interface_yang_name,
            dataplane_yang_name, vrrp_yang_name):

        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        copy_string = copy.deepcopy(dataplane_group_keepalived_config)
        config_string += copy_string
        result = json.dumps(simple_config)
        expect = keepalived_config.convert_to_vci_format(config_string)
        assert result == expect

    def test_config_to_vci_format_fuller_config(
            self, autogeneration_string, max_group_keepalived_config,
            keepalived_config, complex_config):

        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        copy_string = copy.deepcopy(max_group_keepalived_config)
        config_string += copy_string
        result = json.dumps(complex_config)
        expect = keepalived_config.convert_to_vci_format(config_string)
        assert result == expect

    def test_config_to_vci_format_bonding_config(
            self, autogeneration_string, bonding_group_keepalived_config,
            keepalived_config, simple_bonding_config, interface_yang_name,
            bonding_yang_name, vrrp_yang_name):

        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        copy_string = copy.deepcopy(bonding_group_keepalived_config)
        config_string += copy_string

        intf_list = simple_bonding_config[interface_yang_name]
        bonding_intf = intf_list[bonding_yang_name][0][vrrp_yang_name]
        bonding_intf["start-delay"] = "60"
        bonding_intf["vrrp-group"][0]["virtual-address"] = \
            ["10.11.2.100/25"]
        bonding_intf["vrrp-group"][0]["tagnode"] = 2
        del bonding_intf["vrrp-group"][0]["priority"]

        result = json.dumps(simple_bonding_config)
        expect = keepalived_config.convert_to_vci_format(config_string)
        assert result == expect

    def test_config_to_vci_format_dataplane_vif_config(
            self, autogeneration_string,
            dataplane_vif_group_keepalived_config,
            keepalived_config, simple_dataplane_vif_config,
            interface_yang_name, dataplane_yang_name, vrrp_yang_name,
            dataplane_group_keepalived_config, generic_group):

        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        copy_string = copy.deepcopy(dataplane_group_keepalived_config)
        config_string += copy_string
        copy_string = copy.deepcopy(dataplane_vif_group_keepalived_config)
        config_string += copy_string

        intf_level = simple_dataplane_vif_config[interface_yang_name]
        vif_intf = intf_level[dataplane_yang_name][0]["vif"][0]
        vif_group = copy.deepcopy(generic_group)
        vif_group["virtual-address"] = ["10.10.2.100/25"]
        del vif_group["priority"]
        vif_group["tagnode"] = 2
        vif_intf[vrrp_yang_name]["vrrp-group"] = [vif_group]

        result = json.dumps(simple_dataplane_vif_config)
        expect = keepalived_config.convert_to_vci_format(config_string)
        assert result == expect

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

    def test_update_config_no_config(
            self, top_level_dictionary, keepalived_config):
        expected = []
        keepalived_config.update(top_level_dictionary)
        result = keepalived_config.vrrp_instances
        assert expected == result

    def test_update_config_no_vrrp_config(
            self, top_level_dictionary, keepalived_config,
            dataplane_yang_name, second_dataplane_interface):
        expected = []
        config = top_level_dictionary
        config[dataplane_yang_name] = [second_dataplane_interface]
        keepalived_config.update(config)
        result = keepalived_config.vrrp_instances
        assert expected == result

    def test_update_config_error_when_vif_under_intf(
            self, keepalived_config, simple_dataplane_vif_config):
        with pytest.raises(ValueError):
            keepalived_config.update(simple_dataplane_vif_config)

    def test_update_config_disabled_group(
            self, keepalived_config, interface_yang_name,
            dataplane_yang_name, disabled_group,
            dataplane_interface):
        expected = []
        disabled_interface = dataplane_interface
        disabled_interface["vyatta-vrrp-v1:vrrp"]["vrrp-group"] = [
            disabled_group
        ]
        disabled_config = {
            interface_yang_name: {
                dataplane_yang_name: [disabled_interface]
            }
        }
        keepalived_config.update(disabled_config)
        result = keepalived_config.vrrp_instances
        # Contents should be the same, even if the reference
        # isn't
        assert str(result) == str(expected)

    def test_update_config_simple_config(
            self, keepalived_config, simple_config,
            simple_vrrp_group_object):
        expected = [simple_vrrp_group_object]
        keepalived_config.update(simple_config)
        result = keepalived_config.vrrp_instances
        # Contents should be the same, even if the reference
        # isn't
        assert str(result) == str(expected)

    def test_write_config_file_doesnt_exist(self, tmp_path):
        file_path = Path(f"{tmp_path}/test_file")
        result = False
        expected = file_path.exists()
        assert result == expected

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

    def test_convert_authentication_config_config_exists(
            self, keepalived_config):
        expected = {"authentication": {
            "password": "test",
            "type": "plaintext-password"
        }}
        config_block = ['authentication {', "auth_type PASS",
                        "auth_pass test", "}"]

        result = {}
        keepalived_config._convert_authentication_config(
            config_block, result)
        assert result == expected

    def test_convert_authentication_config_no_config(
            self, keepalived_config):
        expected = {}
        config_block = []
        result = {}
        keepalived_config._convert_authentication_config(
            config_block, result)
        assert result == expected

    def test_convert_authentication_config_config_doesnt_exist(
            self, keepalived_config):
        expected = {}
        config_block = ['virtual_ipaddress', "10.10.10.100/25", "}"]
        result = {}
        keepalived_config._convert_authentication_config(
            config_block, result)
        assert result == expected

    def test_convert_notify_proto_config_config_exists(
            self, keepalived_config):
        expected = {"notify": {
            "bgp": [None],
            "ipsec": [None]
        }}
        config_block = ["notify {",
                        "/opt/vyatta/sbin/vyatta-ipsec-notify.sh",
                        "/opt/vyatta/sbin/notify-bgp", "}"]
        result = {}
        keepalived_config._convert_notify_proto_config(
            config_block, result)
        assert result == expected

    def test_convert_notify_proto_config_no_config(
            self, keepalived_config):
        expected = {}
        config_block = []
        result = {}
        keepalived_config._convert_notify_proto_config(
            config_block, result)
        assert result == expected

    def test_convert_notify_proto_config_config_doesnt_exist(
            self, keepalived_config):
        expected = {}
        config_block = ['virtual_ipaddress', "10.10.10.100/25", "}"]
        result = {}
        keepalived_config._convert_notify_proto_config(
            config_block, result)
        assert result == expected

    def test_convert_interface_tracking_config_config_exists(
            self, keepalived_config):
        expected = {"track": {"interface": [
            {"name": "lo1"},
            {"name": "dp0p2",
             "weight": {"type": "decrement", "value": 10}}
        ]}}
        config_block = ["track {",
                        "interface {",
                        "lo1",
                        "dp0p2 weight -10",
                        "}"]
        result = {"track": {}}
        keepalived_config._convert_interface_tracking_config(
            config_block, result, 0)
        assert result == expected

    def test_convert_interface_tracking_config_config_doesnt_exist(
            self, keepalived_config):
        expected = {}
        config_block = ['virtual_ipaddress', "10.10.10.100/25", "}"]
        result = {}
        keepalived_config._convert_interface_tracking_config(
            config_block, result, 0)
        assert result == expected
