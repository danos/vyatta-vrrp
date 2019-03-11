#! /usr/bin/python3

# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import pytest
import copy
import sys


class FakeVci(object):

    class Config(object):
        def set(self, conf):
            pass

    class State(object):
        def get(object):
            pass


class TestKeepalivedConfigFile():

    def test_config_path_default(self, keepalived_config):
        expected = "/etc/keepalived/keepalived.conf"
        result = keepalived_config.config_file_path()
        assert result == expected

    def test_config_path_user_defined(self):
        class FakeVci(object):

            class Config(object):
                def set(self, conf):
                    pass

            class State(object):
                def get(object):
                    pass

        sys.modules['vci'] = FakeVci
        from vyatta.keepalived.config_file import KeepalivedConfig

        expected = "/test/file/path.conf"
        config = KeepalivedConfig("/test/file/path.conf")
        result = config.config_file_path()
        assert result == expected

    def test_implementation_name(self, keepalived_config):
        expected = "Keepalived"
        result = keepalived_config.impl_name()
        assert result == expected

    def test_get_config_indexes_list_autogen(self, autogeneration_string,
                                             keepalived_config):
        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        expected = [6]
        result = keepalived_config._get_config_indexes(
            config_string.splitlines(), "global_defs")
        assert result == expected

    def test_get_config_indexes_list_no_groups(self, autogeneration_string,
                                               keepalived_config):
        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        expected = []
        result = keepalived_config._get_config_indexes(
            config_string.splitlines(), "vrrp_instance")
        assert result == expected

    def test_get_config_indexes_list_single_group(
            self, autogeneration_string, datatplane_group_keepalived_config,
            keepalived_config):
        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        copy_string = copy.deepcopy(datatplane_group_keepalived_config)
        config_string += copy_string
        expected = [13]
        result = keepalived_config._get_config_indexes(
            config_string.splitlines(), "vrrp_instance")
        assert result == expected

    def test_get_config_indexes_list_multiple_groups(
            self, autogeneration_string, datatplane_group_keepalived_config,
            bonding_group_keepalived_config, keepalived_config):
        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        copy_string = copy.deepcopy(datatplane_group_keepalived_config)
        config_string += copy_string
        copy_string = copy.deepcopy(bonding_group_keepalived_config)
        config_string += copy_string
        expected = [13, 25]
        result = keepalived_config._get_config_indexes(
            config_string.splitlines(), "vrrp_instance")
        assert result == expected

    def test_get_config_blocks_autogen(
            self, autogeneration_string, keepalived_config):
        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        expected = [[
            "global_defs {", "enable_traps", "enable_dbus",
            "snmp_socket tcp:localhost:705:1", "enable_snmp_keepalived",
            "enable_snmp_rfc", "}"]]
        result = keepalived_config._get_config_blocks(
            config_string.splitlines(), [6])
        assert result == expected

    def test_get_config_blocks_no_groups(self, autogeneration_string,
                                         keepalived_config):
        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        expected = []
        result = keepalived_config._get_config_blocks(
            config_string.splitlines(), [])
        assert result == expected

    def test_get_config_blocks_single_group(
            self, autogeneration_string, datatplane_group_keepalived_config,
            keepalived_config):
        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        copy_string = copy.deepcopy(datatplane_group_keepalived_config)
        config_string += copy_string
        expected = \
            [
                [
                    "vrrp_instance vyatta-dp0p1s1-1 {", "state BACKUP",
                    "interface dp0p1s1", "virtual_router_id 1", "version 2",
                    "start_delay 0", "priority 100", "advert_int 1",
                    "virtual_ipaddress {", "10.10.1.100/25", "}", "}"
                ]
            ]
        result = keepalived_config._get_config_blocks(
            config_string.splitlines(), [13])
        assert result == expected

    def test_get_config_blocks_multiple_groups(
            self, autogeneration_string, datatplane_group_keepalived_config,
            bonding_group_keepalived_config, keepalived_config):

        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        copy_string = copy.deepcopy(datatplane_group_keepalived_config)
        config_string += copy_string
        copy_string = copy.deepcopy(bonding_group_keepalived_config)
        config_string += copy_string
        expected = \
            [
                [
                    "vrrp_instance vyatta-dp0p1s1-1 {", "state BACKUP",
                    "interface dp0p1s1", "virtual_router_id 1", "version 2",
                    "start_delay 0", "priority 100", "advert_int 1",
                    "virtual_ipaddress {", "10.10.1.100/25", "}", "}"
                ],
                [
                    "vrrp_instance vyatta-dp0bond0-2 {", "state BACKUP",
                    "interface dp0bond0", "virtual_router_id 2", "version 2",
                    "start_delay 60", "priority 100", "advert_int 1",
                    "virtual_ipaddress {", "10.11.2.100/25", "}", "}"
                ]
            ]
        result = keepalived_config._get_config_blocks(
            config_string.splitlines(), [13, 25])
        assert result == expected

    def test_find_config_value_autogen_key_value_defined_entry(
            self, keepalived_config):
        config_list = [[
            "global_defs {", "enable_traps", "enable_dbus",
            "snmp_socket tcp:localhost:705:1", "enable_snmp_keepalived",
            "enable_snmp_rfc", "}"]]
        expected = (True, "tcp:localhost:705:1")
        for block in config_list:
            result = keepalived_config._find_config_value(block, "snmp_socket")
            assert result == expected

    def test_find_config_value_autogen_key_value_undefined_entry(
            self, keepalived_config):
        config_list = [[
            "global_defs {", "enable_traps", "enable_dbus",
            "snmp_socket tcp:localhost:705:1", "enable_snmp_keepalived",
            "enable_snmp_rfc", "}"]]
        expected = (False, "NOTFOUND")
        for block in config_list:
            result = keepalived_config._find_config_value(
                block, "Alice_in_wonderland")
            assert result == expected

    def test_find_config_value_autogen_presence_defined_entry(
            self, keepalived_config):
        config_list = [[
            "global_defs {", "enable_traps", "enable_dbus",
            "snmp_socket tcp:localhost:705:1", "enable_snmp_keepalived",
            "enable_snmp_rfc", "}"]]
        expected = (True, [None])
        for block in config_list:
            result = keepalived_config._find_config_value(block, "enable_dbus")
            assert result == expected

    def test_find_config_value_autogen_presence_undefined_entry(
            self, keepalived_config):
        config_list = [[
            "global_defs {", "enable_traps", "enable_dbus",
            "snmp_socket tcp:localhost:705:1", "enable_snmp_keepalived",
            "enable_snmp_rfc", "}"]]
        expected = (False, "NOTFOUND")
        for block in config_list:
            result = keepalived_config._find_config_value(
                block, "The_two_towers")
            assert result == expected

    def test_find_config_value_single_group_defined_entry(
            self, keepalived_config):
        config_list = \
            [
                [
                    "vrrp_instance vyatta-dp0p1s1-1 {", "state BACKUP",
                    "interface dp0p1s1", "virtual_router_id 1", "version 2",
                    "start_delay 0", "priority 100", "advert_int 1",
                    "virtual_ipaddress {", "10.10.1.100/25", "}", "}"
                ]
            ]
        expected = (True, "BACKUP")
        for block in config_list:
            result = keepalived_config._find_config_value(block, "state")
            assert result == expected

    def test_find_config_value_single_group_undefined_entry(
            self, keepalived_config):
        config_list = \
            [
                [
                    "vrrp_instance vyatta-dp0p1s1-1 {", "state BACKUP",
                    "interface dp0p1s1", "virtual_router_id 1", "version 2",
                    "start_delay 0", "priority 100", "advert_int 1",
                    "virtual_ipaddress {", "10.10.1.100/25", "}", "}"
                ]
            ]
        expected = (False, "NOTFOUND")
        for block in config_list:
            result = keepalived_config._find_config_value(
                block, "There_and_back_again")
            assert result == expected

    def test_find_config_value_multiple_group_defined_entry(
            self, keepalived_config):
        config_list = \
            [
                [
                    "vrrp_instance vyatta-dp0p1s1-1 {", "state BACKUP",
                    "interface dp0p1s1", "virtual_router_id 1", "version 2",
                    "start_delay 0", "priority 100", "advert_int 1",
                    "virtual_ipaddress {", "10.10.1.100/25", "}", "}"
                ],
                [
                    "vrrp_instance vyatta-dp0bond0-2 {", "state BACKUP",
                    "interface dp0bond0", "virtual_router_id 2", "version 2",
                    "start_delay 60", "priority 100", "advert_int 1",
                    "virtual_ipaddress {", "10.11.2.100/25", "}", "}"
                ]
            ]
        expected = (True, "BACKUP")
        for block in config_list:
            result = keepalived_config._find_config_value(block, "state")
            assert result == expected

    def test_find_config_value_multiple_group_undefined_entry(
            self, keepalived_config):
        config_list = \
            [
                [
                    "vrrp_instance vyatta-dp0p1s1-1 {", "state BACKUP",
                    "interface dp0p1s1", "virtual_router_id 1", "version 2",
                    "start_delay 0", "priority 100", "advert_int 1",
                    "virtual_ipaddress {", "10.10.1.100/25", "}", "}"
                ],
                [
                    "vrrp_instance vyatta-dp0bond0-2 {", "state BACKUP",
                    "interface dp0bond0", "virtual_router_id 2", "version 2",
                    "start_delay 60", "priority 100", "advert_int 1",
                    "virtual_ipaddress {", "10.11.2.100/25", "}", "}"
                ]
            ]
        expected = (False, "NOTFOUND")
        for block in config_list:
            result = keepalived_config._find_config_value(
                block, "A_tale_of_two_cities")
            assert result == expected

    def test_find_config_value_multiple_group_presence_defined_entry(
            self, keepalived_config):
        config_list = \
            [
                [
                    "vrrp_instance vyatta-dp0p1s1-1 {", "state BACKUP",
                    "interface dp0p1s1", "virtual_router_id 1", "version 2",
                    "start_delay 0", "priority 100", "advert_int 1",
                    "virtual_ipaddress {", "10.10.1.100/25", "}",
                    "vmac_xmit_base", "}"
                ],
                [
                    "vrrp_instance vyatta-dp0bond0-2 {", "state BACKUP",
                    "interface dp0bond0", "virtual_router_id 2", "version 2",
                    "start_delay 60", "priority 100", "advert_int 1",
                    "virtual_ipaddress {", "10.11.2.100/25", "}",
                    "vmac_xmit_base", "}"
                ]
            ]
        expected = (True, [None])
        for block in config_list:
            result = keepalived_config._find_config_value(
                block, "vmac_xmit_base")
            assert result == expected

    def test_find_interface_in_yang_dataplane_list_empty(
            self, keepalived_config, interface_yang_name,
            dataplane_yang_name, simple_config, dataplane_interface):
        simple_config[interface_yang_name][dataplane_yang_name] = []
        interface_list = \
            simple_config[interface_yang_name][dataplane_yang_name]
        result = keepalived_config._find_interface_in_yang_repr(
            "dp0p1s1", "", interface_list)
        expected = dataplane_interface
        expected["vyatta-vrrp-v1:vrrp"]["vrrp-group"] = []
        assert result == expected
        assert result is \
            simple_config[interface_yang_name][dataplane_yang_name][0]

    def test_find_interface_in_yang_dataplane_intf_exists(
            self, keepalived_config, interface_yang_name,
            dataplane_yang_name, simple_config):
        interface_list = \
            simple_config[interface_yang_name][dataplane_yang_name]
        result = keepalived_config._find_interface_in_yang_repr(
            "dp0p1s1", "", interface_list)
        expected = simple_config[interface_yang_name][dataplane_yang_name][0]
        assert result is expected

    def test_find_interface_in_yang_dataplane_intf_doesnt_exist(
            self, keepalived_config, interface_yang_name,
            dataplane_yang_name, simple_config, second_dataplane_interface):
        interface_list = \
            simple_config[interface_yang_name][dataplane_yang_name]
        result = keepalived_config._find_interface_in_yang_repr(
            "dp0p1s2", "", interface_list)
        expected = second_dataplane_interface
        expected["vyatta-vrrp-v1:vrrp"]["vrrp-group"] = []
        assert result == expected
        assert result is \
            simple_config[interface_yang_name][dataplane_yang_name][1]

    def test_find_interface_in_yang_dataplane_intf_exist_vif_doesnt_exist(
            self, keepalived_config, interface_yang_name,
            dataplane_yang_name, simple_config, vif_dataplane_interface):
        interface_list = \
            simple_config[interface_yang_name][dataplane_yang_name]
        result = keepalived_config._find_interface_in_yang_repr(
            "dp0p1s1", "10", interface_list)
        expected = vif_dataplane_interface
        expected["vyatta-vrrp-v1:vrrp"]["vrrp-group"] = []
        yang_repr_dataplane_list = interface_list
        assert result == expected
        assert result is \
            yang_repr_dataplane_list[0]["vif"][0]

    def test_find_interface_in_yang_datapln_intf_doesnt_exist_vif_doesnt_exist(
            self, keepalived_config, interface_yang_name,
            dataplane_yang_name, simple_config, vif_dataplane_interface):
        interface_list = \
            simple_config[interface_yang_name][dataplane_yang_name]
        result = keepalived_config._find_interface_in_yang_repr(
            "dp0p1s2", "10", interface_list)
        expected = vif_dataplane_interface
        expected["vyatta-vrrp-v1:vrrp"]["vrrp-group"] = []
        yang_repr_dataplane_list = \
            simple_config[interface_yang_name][dataplane_yang_name]
        assert result == expected
        assert result is \
            yang_repr_dataplane_list[1]["vif"][0]

    def test_find_interface_in_yang_datapln_intf_exist_multiple_vif_exist(
            self, keepalived_config, interface_yang_name,
            dataplane_yang_name, simple_config, vif_dataplane_interface):
        interface_list = \
            simple_config[interface_yang_name][dataplane_yang_name]
        interface_list[0]["vif"] = [vif_dataplane_interface]
        result = keepalived_config._find_interface_in_yang_repr(
            "dp0p1s1", "20", interface_list)
        expected = vif_dataplane_interface
        expected["tagnode"] = "20"
        expected["vyatta-vrrp-v1:vrrp"]["vrrp-group"] = []
        yang_repr_dataplane_list = interface_list
        assert result == expected
        assert result is \
            yang_repr_dataplane_list[0]["vif"][1]
