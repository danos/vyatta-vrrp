#! /usr/bin/python3

import copy

import pytest

import vyatta.vrrp_vci.keepalived.util as util


class TestKeepalivedUtils:

    @pytest.mark.parametrize(
        "expected,actual",
        [
            (
                "vyatta-interfaces-v1:interfaces",
                util.INTERFACE_YANG_NAME
            ),
            (
                "vyatta-interfaces-dataplane-v1:dataplane",
                util.DATAPLANE_YANG_NAME
            ),
            (
                "vyatta-vrrp-v1:vrrp",
                util.VRRP_YANG_NAME
            ),
            (
                "vyatta-bonding-v1:bonding",
                util.BONDING_YANG_NAME
            ),
            (
                "vyatta-interfaces-switch-v1:switch",
                util.SWITCH_YANG_NAME
            ),
            (
                "vif",
                util.VIF_YANG_NAME
            ),
            (
                "vyatta-vrrp-path-monitor-track-interfaces-dataplane" +
                "-v1:path-monitor",
                util.PATHMON_DATAPLANE_YANG_NAME
            ),
            (
                "vyatta-vrrp-path-monitor-track-interfaces-bonding" +
                "-v1:path-monitor",
                util.PATHMON_BONDING_YANG_NAME
            ),
            (
                "vyatta-vrrp-route-to-track-interfaces-dataplane" +
                "-v1:route-to",
                util.ROUTE_DATAPLANE_YANG_NAME
            ),
            (
                "vyatta-vrrp-route-to-track-interfaces-bonding" +
                "-v1:route-to",
                util.ROUTE_BONDING_YANG_NAME
            ),
            (
                "org.freedesktop.DBus.Properties",
                util.PROPERTIES_DBUS_INTF_NAME,
            ),
            (
                "org.freedesktop.systemd1",
                util.SYSTEMD_DBUS_INTF_NAME
            ),
            (
                "/org/freedesktop/systemd1",
                util.SYSTEMD_DBUS_PATH
            ),
            (
                "org.freedesktop.systemd1.Manager",
                util.SYSTEMD_MANAGER_DBUS_INTF_NAME
            ),
            (
                "org.freedesktop.systemd1.Unit",
                util.SYSTEMD_UNIT_DBUS_NAME
            ),
            (
                "org.keepalived.Vrrp1",
                util.KEEPALIVED_DBUS_INTF_NAME
            ),
            (
                "/org/keepalived/Vrrp1/Vrrp",
                util.VRRP_PROCESS_DBUS_INTF_PATH
            ),
            (
                "org.keepalived.Vrrp1.Instance",
                util.VRRP_INSTANCE_DBUS_INTF_NAME
            ),
            (
                "/org/keepalived/Vrrp1/Instance",
                util.VRRP_INSTANCE_DBUS_PATH
            )
        ],
        ids=[
            "Interface yang name", "Dataplane yang name",
            "Vrrp yang name", "Bonding yang name",
            "Switch yang name", "Vif yang name",
            "Path monitor dataplane yang name",
            "Path monitor bonding yang name",
            "Route to dataplane yang name",
            "Route to monitor bonding yang name",
            "DBus properties name",
            "DBus systemd interface name",
            "DBus systemd path name",
            "DBus systemd manager interface name",
            "DBus systemd unit interface name",
            "DBus keepalived interface name",
            "DBus VRRP process interface path",
            "DBus VRRP Group instance interface name",
            "DBus VRRP Group instance path"
        ]
    )
    def test_generated_constants(self, expected, actual):
        assert expected == actual

    def test_get_hello_sources_no_hellos(
            self, simple_config):
        expected = []
        result = util.get_hello_sources(simple_config)
        assert expected == result

    @pytest.mark.sanity
    def test_get_hello_sources(
            self, simple_config, interface_yang_name,
            dataplane_yang_name, vrrp_yang_name):
        expected = [
            [
                "10.1.1.1",
                "interfaces dataplane dp0p1s1 vrrp vrrp-group 1" +
                " hello-source-address 10.1.1.1"
            ]
        ]
        intf = simple_config[interface_yang_name][dataplane_yang_name][0]
        intf[vrrp_yang_name]["vrrp-group"][0]["hello-source-address"] = \
            "10.1.1.1"
        result = util.get_hello_sources(simple_config)
        assert expected == result

    @pytest.mark.sanity
    def test_get_hello_sources_vifs(
            self, simple_config, interface_yang_name,
            dataplane_yang_name, vrrp_yang_name, generic_group):
        vif_config = copy.deepcopy(simple_config)
        expected = [
            [
                "10.1.1.1",
                "interfaces dataplane dp0p1s1 vif 10 vrrp vrrp-group 1" +
                " hello-source-address 10.1.1.1"
            ]
        ]
        del vif_config[interface_yang_name][dataplane_yang_name]
        vif_config[interface_yang_name]["vif"] = [
            {"tagnode": "dp0p1s1.10",
             vrrp_yang_name: {"vrrp-group": [copy.deepcopy(generic_group)]}}
        ]
        intf = vif_config[interface_yang_name]["vif"][0]
        intf[vrrp_yang_name]["vrrp-group"][0]["hello-source-address"] = \
            "10.1.1.1"
        result = util.get_hello_sources(vif_config)
        assert expected == result

    @pytest.mark.sanity
    def test_is_local_address_ipv4(self):
        expected = None
        ipaddress = "127.0.0.1"
        util.is_local_address(ipaddress)
        result = None
        assert expected == result

    @pytest.mark.sanity
    def test_is_local_address_ipv6(self):
        expected = None
        ipaddress = "::1"
        util.is_local_address(ipaddress)
        result = None
        assert expected == result

    @pytest.mark.sanity
    def test_is_local_address_not_local(self):
        ipaddress = "10.1.1.1"
        with pytest.raises(OSError):
            util.is_local_address(ipaddress)

    @pytest.mark.sanity
    def test_is_rfc_compat_configured_no(
            self, simple_config):
        expected = (False, [])
        result = util.is_rfc_compat_configured(simple_config)
        assert expected == result

    @pytest.mark.sanity
    def test_is_rfc_compat_configured_yes(
            self, complex_config):
        expected = (
            True,
            [
                [
                    [None],
                    'interfaces dataplane dp0p1s1 vrrp vrrp-group 1 ' +
                    'rfc-compatibility [None]'
                ]
            ]
        )
        result = util.is_rfc_compat_configured(complex_config)
        assert expected == result

    def test_running_on_vmware_baremetal(
            self, mock_show_version_rpc_no_hypervisor):
        expected = False
        result = util.running_on_vmware()
        assert expected == result

    def test_running_on_vmware_no(
            self, mock_show_version_rpc_kvm):
        expected = False
        result = util.running_on_vmware()
        assert expected == result

    def test_running_on_vmware_yes(
            self, mock_show_version_rpc_vmware):
        expected = True
        result = util.running_on_vmware()
        assert expected == result

    @pytest.mark.sanity
    def test_sanitize_vrrp_config_one_configured(self,
                                                 simple_config):
        result = util.sanitize_vrrp_config(simple_config)
        expected =\
            {
                "vyatta-interfaces-v1:interfaces": {
                    "vyatta-interfaces-dataplane-v1:dataplane":
                        [
                            {
                                "tagnode": "dp0p1s1",
                                "vyatta-vrrp-v1:vrrp": {
                                    "start-delay": 0,
                                    "vrrp-group": [
                                        {
                                            "accept": False,
                                            "preempt": True,
                                            "priority": 200,
                                            "tagnode": 1,
                                            "version": 2,
                                            "virtual-address": [
                                                "10.10.1.100/25"
                                            ]
                                        }
                                    ]
                                }
                            }
                        ]
                }
            }
        assert result == expected

    def test_sanitize_vrrp_config_one_not_configured(self,
                                                     interface_yang_name,
                                                     dataplane_yang_name):
        expected =\
            {interface_yang_name: {}}
        test_conf =\
            {
                interface_yang_name: {
                    dataplane_yang_name: [
                        {
                            "tagnode": "dp0p1s1",
                            "vyatta-vrrp-v1:vrrp": {
                                "start-delay": 0
                            }
                        }
                    ]
                }
            }
        assert test_conf != expected
        result = util.sanitize_vrrp_config(test_conf)
        assert result == expected

    def test_sanitize_vrrp_config_one_configured_one_not_configured(
            self, simple_config, second_dataplane_interface,
            interface_yang_name, dataplane_yang_name):
        expected =\
            {
                "vyatta-interfaces-v1:interfaces": {
                    "vyatta-interfaces-dataplane-v1:dataplane": [
                        {
                            "tagnode": "dp0p1s1",
                            "vyatta-vrrp-v1:vrrp": {
                                "start-delay": 0,
                                "vrrp-group": [
                                    {
                                        "accept": False,
                                        "preempt": True,
                                        "priority": 200,
                                        "tagnode": 1,
                                        "version": 2,
                                        "virtual-address": [
                                            "10.10.1.100/25"
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        test_conf = simple_config
        test_conf[interface_yang_name][dataplane_yang_name]\
            .append(second_dataplane_interface)
        assert test_conf != expected
        result = util.sanitize_vrrp_config(test_conf)
        assert result == expected

    def test_sanitize_vrrp_config_two_intf_type(self, simple_config,
                                                bonding_list,
                                                interface_yang_name,
                                                dataplane_yang_name,
                                                bonding_yang_name,
                                                second_dataplane_interface):
        expected = copy.deepcopy(simple_config)
        expected[interface_yang_name][bonding_yang_name]\
            = bonding_list
        test_conf = copy.deepcopy(simple_config)
        test_conf[interface_yang_name][dataplane_yang_name]\
            .append(second_dataplane_interface)
        test_conf[interface_yang_name][bonding_yang_name] =\
            bonding_list
        assert test_conf != expected
        result = util.sanitize_vrrp_config(test_conf)
        assert result == expected

    @pytest.mark.sanity
    def test_sanitize_vrrp_config_remove_empty_vif(self, simple_config,
                                                   interface_yang_name,
                                                   dataplane_yang_name,
                                                   vif_dataplane_list):
        expected = copy.deepcopy(simple_config)
        test_conf = copy.deepcopy(simple_config)
        test_conf[interface_yang_name][dataplane_yang_name][0]["vif"]\
            = vif_dataplane_list
        result = util.sanitize_vrrp_config(test_conf)
        assert expected == result

    def test_sanitize_vrrp_config_move_dataplane_vif(
            self, simple_config, interface_yang_name,
            dataplane_yang_name, generic_group,
            vif_dataplane_list_sanitized,
            vif_dataplane_list):
        expected = copy.deepcopy(simple_config)
        test_conf = copy.deepcopy(simple_config)
        expected[interface_yang_name]["vif"] =\
            vif_dataplane_list_sanitized
        first_intf = test_conf[interface_yang_name][dataplane_yang_name][0]
        first_intf["vif"] = vif_dataplane_list
        first_intf["vif"][0]["vyatta-vrrp-v1:vrrp"]["vrrp-group"]\
            = [generic_group]
        result = util.sanitize_vrrp_config(test_conf)
        assert expected == result

    def test_sanitize_vrrp_config_move_bonding_vif(self, simple_config,
                                                   interface_yang_name,
                                                   bonding_yang_name,
                                                   bonding_list,
                                                   generic_group,
                                                   vif_bonding_list,
                                                   vif_bonding_list_sanitized):
        expected = copy.deepcopy(simple_config)
        expected[interface_yang_name][bonding_yang_name]\
            = bonding_list
        expected[interface_yang_name]["vif"] =\
            vif_bonding_list_sanitized
        test_conf = copy.deepcopy(simple_config)
        test_conf[interface_yang_name][bonding_yang_name] =\
            bonding_list
        test_conf[interface_yang_name][bonding_yang_name][0]["vif"] =\
            vif_bonding_list
        first_intf = test_conf[interface_yang_name][bonding_yang_name][0]
        first_intf["vif"][0]["vyatta-vrrp-v1:vrrp"]["vrrp-group"]\
            = [generic_group]
        result = util.sanitize_vrrp_config(test_conf)
        assert expected == result

    def test_sanitize_vrrp_config_move_switch_vif(
            self, simple_config, interface_yang_name,
            switch_yang_name, generic_group,
            vif_switch_list_sanitized,
            switch_list, dataplane_yang_name):
        expected = copy.deepcopy(simple_config)
        test_conf = copy.deepcopy(simple_config)
        del expected[interface_yang_name][dataplane_yang_name]
        del test_conf[interface_yang_name][dataplane_yang_name]
        expected[interface_yang_name]["vif"] = \
            vif_switch_list_sanitized
        test_conf[interface_yang_name][switch_yang_name] = switch_list
        first_intf = test_conf[interface_yang_name][switch_yang_name][0]
        first_intf["vif"][0]["vyatta-vrrp-v1:vrrp"]["vrrp-group"]\
            = [generic_group]
        result = util.sanitize_vrrp_config(test_conf)
        assert expected == result

    @pytest.mark.sanity
    def test_sanitize_vrrp_config_move_two_intf_types_vif(
            self, simple_config, interface_yang_name, dataplane_yang_name,
            bonding_list, bonding_yang_name, vif_dataplane_list,
            vif_two_type_list_sanitized, generic_group,
            vif_bonding_list):
        expected = copy.deepcopy(simple_config)
        expected[interface_yang_name][bonding_yang_name]\
            = bonding_list
        expected[interface_yang_name]["vif"] =\
            vif_two_type_list_sanitized
        test_conf = copy.deepcopy(simple_config)
        test_conf[interface_yang_name][dataplane_yang_name][0]["vif"]\
            = vif_dataplane_list
        first_intf = test_conf[interface_yang_name][dataplane_yang_name][0]
        first_intf["vif"][0]["vyatta-vrrp-v1:vrrp"]["vrrp-group"]\
            = [generic_group]
        test_conf[interface_yang_name][bonding_yang_name] =\
            bonding_list
        test_conf[interface_yang_name][bonding_yang_name][0]["vif"] =\
            vif_bonding_list
        second_intf = test_conf[interface_yang_name][bonding_yang_name][0]
        second_intf["vif"][0]["vyatta-vrrp-v1:vrrp"]["vrrp-group"]\
            = [generic_group]
        result = util.sanitize_vrrp_config(test_conf)
        assert expected == result

    def test_get_config_indexes_list_autogen(self, autogeneration_string):
        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        expected = [6]
        result = util.get_config_indexes(
            config_string.splitlines(), "global_defs")
        assert result == expected

    def test_get_config_indexes_list_no_groups(self,
                                               autogeneration_string,):
        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        expected = []
        result = util.get_config_indexes(
            config_string.splitlines(), "vrrp_instance")
        assert result == expected

    def test_get_config_indexes_list_single_group(
            self, autogeneration_string,
            dataplane_group_keepalived_config):
        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        copy_string = copy.deepcopy(dataplane_group_keepalived_config)
        config_string += copy_string
        expected = [13]
        result = util.get_config_indexes(
            config_string.splitlines(), "vrrp_instance")
        assert result == expected

    def test_get_config_indexes_list_multiple_groups(
            self, autogeneration_string, dataplane_group_keepalived_config,
            bonding_group_keepalived_config):
        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        copy_string = copy.deepcopy(dataplane_group_keepalived_config)
        config_string += copy_string
        copy_string = copy.deepcopy(bonding_group_keepalived_config)
        config_string += copy_string
        expected = [13, 25]
        result = util.get_config_indexes(
            config_string.splitlines(), "vrrp_instance")
        assert result == expected

    def test_get_config_blocks_autogen(
            self, autogeneration_string):
        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        expected = [[
            "global_defs {", "enable_traps", "enable_dbus",
            "snmp_socket tcp:localhost:705:1", "enable_snmp_keepalived",
            "enable_snmp_rfc", "}"]]
        result = util.get_config_blocks(
            config_string.splitlines(), [6])
        assert result == expected

    def test_get_config_blocks_no_groups(self, autogeneration_string):
        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        expected = []
        result = util.get_config_blocks(
            config_string.splitlines(), [])
        assert result == expected

    def test_get_config_blocks_single_group(
            self, autogeneration_string,
            dataplane_group_keepalived_config):
        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        copy_string = copy.deepcopy(dataplane_group_keepalived_config)
        config_string += copy_string
        expected = \
            [
                [
                    "vrrp_instance vyatta-dp0p1s1-1 {", "state BACKUP",
                    "interface dp0p1s1", "virtual_router_id 1", "version 2",
                    "start_delay 0", "priority 200", "advert_int 1",
                    "virtual_ipaddress {", "10.10.1.100/25", "}", "}"
                ]
            ]
        result = util.get_config_blocks(
            config_string.splitlines(), [13])
        assert result == expected

    def test_get_config_blocks_multiple_groups(
            self, autogeneration_string, dataplane_group_keepalived_config,
            bonding_group_keepalived_config):

        copy_string = copy.deepcopy(autogeneration_string)
        config_string = copy_string
        copy_string = copy.deepcopy(dataplane_group_keepalived_config)
        config_string += copy_string
        copy_string = copy.deepcopy(bonding_group_keepalived_config)
        config_string += copy_string
        expected = \
            [
                [
                    "vrrp_instance vyatta-dp0p1s1-1 {", "state BACKUP",
                    "interface dp0p1s1", "virtual_router_id 1", "version 2",
                    "start_delay 0", "priority 200", "advert_int 1",
                    "virtual_ipaddress {", "10.10.1.100/25", "}", "}"
                ],
                [
                    "vrrp_instance vyatta-dp0bond0-2 {", "state BACKUP",
                    "interface dp0bond0", "virtual_router_id 2", "version 2",
                    "start_delay 60", "priority 100", "advert_int 1",
                    "virtual_ipaddress {", "10.11.2.100/25", "}", "}"
                ]
            ]
        result = util.get_config_blocks(
            config_string.splitlines(), [13, 25])
        assert result == expected

    def test_find_config_value_autogen_key_value_defined_entry(self):
        config_list = [[
            "global_defs {", "enable_traps", "enable_dbus",
            "snmp_socket tcp:localhost:705:1", "enable_snmp_keepalived",
            "enable_snmp_rfc", "}"]]
        expected_name = "CONFIGURED"
        expected_value = "tcp:localhost:705:1"
        for block in config_list:
            result = util.find_config_value(block, "snmp_socket")
            assert result.name == expected_name
            assert result.value == expected_value

    def test_find_config_value_autogen_key_value_undefined_entry(self):
        config_list = [[
            "global_defs {", "enable_traps", "enable_dbus",
            "snmp_socket tcp:localhost:705:1", "enable_snmp_keepalived",
            "enable_snmp_rfc", "}"]]
        expected_name = "MISSING"
        expected_value = "NOTFOUND"
        for block in config_list:
            result = util.find_config_value(
                block, "Alice_in_wonderland")
            assert result.name == expected_name
            assert result.value == expected_value

    def test_find_config_value_autogen_presence_defined_entry(self):
        config_list = [[
            "global_defs {", "enable_traps", "enable_dbus",
            "snmp_socket tcp:localhost:705:1", "enable_snmp_keepalived",
            "enable_snmp_rfc", "}"]]
        expected_name = "PRESENT"
        expected_value = [None]
        for block in config_list:
            result = util.find_config_value(block, "enable_dbus")
            assert result.name == expected_name
            assert result.value == expected_value

    def test_find_config_value_autogen_presence_undefined_entry(self):
        config_list = [[
            "global_defs {", "enable_traps", "enable_dbus",
            "snmp_socket tcp:localhost:705:1", "enable_snmp_keepalived",
            "enable_snmp_rfc", "}"]]
        expected_name = "MISSING"
        expected_value = "NOTFOUND"
        for block in config_list:
            result = util.find_config_value(
                block, "The_two_towers")
            assert result.name == expected_name
            assert result.value == expected_value

    def test_find_config_value_single_group_defined_entry(self):
        config_list = \
            [
                [
                    "vrrp_instance vyatta-dp0p1s1-1 {", "state BACKUP",
                    "interface dp0p1s1", "virtual_router_id 1", "version 2",
                    "start_delay 0", "priority 100", "advert_int 1",
                    "virtual_ipaddress {", "10.10.1.100/25", "}", "}"
                ]
            ]
        expected_name = "CONFIGURED"
        expected_value = "BACKUP"
        for block in config_list:
            result = util.find_config_value(block, "state")
            assert result.name == expected_name
            assert result.value == expected_value

    def test_find_config_value_over_lapping_default(self):
        config_list = \
            [
                [
                    "vrrp_instance vyatta-dp0p1s1-1 {", "state BACKUP",
                    "interface dp0p1s1", "virtual_router_id 1", "version 2",
                    "start_delay 0", "priority 100", "advert_int 1",
                    "preempt_delay 10",
                    "virtual_ipaddress {", "10.10.1.100/25", "}", "}"
                ]
            ]
        expected_name = "MISSING"
        expected_value = "NOTFOUND"
        for block in config_list:
            result = util.find_config_value(block, "preempt")
            assert result.name == expected_name
            assert result.value == expected_value

    def test_find_config_value_overwrite_default(self):
        config_list = \
            [
                [
                    "vrrp_instance vyatta-dp0p1s1-1 {", "state BACKUP",
                    "interface dp0p1s1", "virtual_router_id 1", "version 2",
                    "start_delay 0", "priority 100", "advert_int 1",
                    "preempt False",
                    "virtual_ipaddress {", "10.10.1.100/25", "}", "}"
                ]
            ]
        expected_name = "CONFIGURED"
        expected_value = "False"
        for block in config_list:
            result = util.find_config_value(block, "preempt")
            assert result.name == expected_name
            assert result.value == expected_value

    def test_find_config_value_single_group_undefined_entry(self):
        config_list = \
            [
                [
                    "vrrp_instance vyatta-dp0p1s1-1 {", "state BACKUP",
                    "interface dp0p1s1", "virtual_router_id 1", "version 2",
                    "start_delay 0", "priority 100", "advert_int 1",
                    "virtual_ipaddress {", "10.10.1.100/25", "}", "}"
                ]
            ]
        expected_name = "MISSING"
        expected_value = "NOTFOUND"
        for block in config_list:
            result = util.find_config_value(
                block, "There_and_back_again")
            assert result.name == expected_name
            assert result.value == expected_value

    def test_find_config_value_multiple_group_defined_entry(self):
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
        expected_name = "CONFIGURED"
        expected_value = "BACKUP"
        for block in config_list:
            result = util.find_config_value(block, "state")
            assert result.name == expected_name
            assert result.value == expected_value

    def test_find_config_value_multiple_group_undefined_entry(self):
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
        expected_name = "MISSING"
        expected_value = "NOTFOUND"
        for block in config_list:
            result = util.find_config_value(
                block, "A_tale_of_two_cities")
            assert result.name == expected_name
            assert result.value == expected_value

    @pytest.mark.sanity
    def test_find_config_value_multiple_group_presence_defined_entry(
            self):
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
        expected_name = "PRESENT"
        expected_value = [None]
        for block in config_list:
            result = util.find_config_value(
                block, "vmac_xmit_base")
            assert result.name == expected_name
            assert result.value == expected_value

    def test_find_interface_in_yang_dataplane_list_empty(
            self, interface_yang_name,
            dataplane_yang_name, simple_config, dataplane_interface):
        simple_config[interface_yang_name][dataplane_yang_name] = []
        interface_list = \
            simple_config[interface_yang_name][dataplane_yang_name]
        result = util.find_interface_in_yang_repr(
            "dp0p1s1", "", interface_list)
        expected = dataplane_interface
        expected["vyatta-vrrp-v1:vrrp"]["vrrp-group"] = []
        assert result == expected
        assert result is \
            simple_config[interface_yang_name][dataplane_yang_name][0]

    @pytest.mark.sanity
    def test_find_interface_in_yang_dataplane_intf_exists(
            self, interface_yang_name,
            dataplane_yang_name, simple_config):
        interface_list = \
            simple_config[interface_yang_name][dataplane_yang_name]
        result = util.find_interface_in_yang_repr(
            "dp0p1s1", "", interface_list)
        expected = simple_config[interface_yang_name][dataplane_yang_name][0]
        assert result is expected

    @pytest.mark.sanity
    def test_find_interface_in_yang_dataplane_intf_doesnt_exist(
            self, interface_yang_name,
            dataplane_yang_name, simple_config, second_dataplane_interface):
        interface_list = \
            simple_config[interface_yang_name][dataplane_yang_name]
        result = util.find_interface_in_yang_repr(
            "dp0p1s2", "", interface_list)
        expected = second_dataplane_interface
        expected["vyatta-vrrp-v1:vrrp"]["vrrp-group"] = []
        assert result == expected
        assert result is \
            simple_config[interface_yang_name][dataplane_yang_name][1]

    def test_find_interface_in_yang_dataplane_intf_exist_vif_doesnt_exist(
            self, interface_yang_name,
            dataplane_yang_name, simple_config, vif_dataplane_interface):
        interface_list = \
            simple_config[interface_yang_name][dataplane_yang_name]
        result = util.find_interface_in_yang_repr(
            "dp0p1s1", "10", interface_list)
        expected = vif_dataplane_interface
        expected["vyatta-vrrp-v1:vrrp"]["vrrp-group"] = []
        yang_repr_dataplane_list = interface_list
        assert result == expected
        assert result is \
            yang_repr_dataplane_list[0]["vif"][0]

    def test_find_interface_in_yang_datapln_intf_doesnt_exist_vif_doesnt_exist(
            self, interface_yang_name,
            dataplane_yang_name, simple_config, vif_dataplane_interface):
        interface_list = \
            simple_config[interface_yang_name][dataplane_yang_name]
        result = util.find_interface_in_yang_repr(
            "dp0p1s2", "10", interface_list)
        expected = vif_dataplane_interface
        expected["vyatta-vrrp-v1:vrrp"]["vrrp-group"] = []
        yang_repr_dataplane_list = \
            simple_config[interface_yang_name][dataplane_yang_name]
        assert result == expected
        assert result is \
            yang_repr_dataplane_list[1]["vif"][0]

    @pytest.mark.sanity
    def test_find_interface_in_yang_datapln_intf_exist_multiple_vif_exist(
            self, interface_yang_name,
            dataplane_yang_name, simple_config, vif_dataplane_interface):
        interface_list = \
            simple_config[interface_yang_name][dataplane_yang_name]
        interface_list[0]["vif"] = [vif_dataplane_interface]
        result = util.find_interface_in_yang_repr(
            "dp0p1s1", "20", interface_list)
        expected = vif_dataplane_interface
        expected["tagnode"] = "20"
        expected["vyatta-vrrp-v1:vrrp"]["vrrp-group"] = []
        yang_repr_dataplane_list = interface_list
        assert result == expected
        assert result is \
            yang_repr_dataplane_list[0]["vif"][1]

    def test_find_interface_in_yang_datapln_intf_same_vif_multi_groups(
            self, interface_yang_name,
            dataplane_yang_name, simple_config, vif_dataplane_interface,
            generic_group):
        interface_list = \
            simple_config[interface_yang_name][dataplane_yang_name]

        multi_vif_groups = copy.deepcopy(vif_dataplane_interface)
        multi_vif_groups["vrrp-group"] = \
            copy.deepcopy(generic_group)
        interface_list[0]["vif"] = [multi_vif_groups]
        result = util.find_interface_in_yang_repr(
            "dp0p1s1", "10", interface_list)
        expected = multi_vif_groups
        yang_repr_dataplane_list = interface_list
        assert result == expected
        assert result is \
            yang_repr_dataplane_list[0]["vif"][0]

    def test_intf_name_to_type_bonding(self, bonding_yang_name):
        expected_yang = bonding_yang_name
        expected_string = "bonding"
        result = util.intf_name_to_type("dp0bond1")
        assert expected_yang == result[0]
        assert expected_string == result[1].name

    def test_intf_name_to_type_switch(self, switch_yang_name):
        expected_yang = switch_yang_name
        expected_string = "switch"
        result = util.intf_name_to_type("sw0")
        assert expected_yang == result[0]
        assert expected_string == result[1].name

    def test_intf_name_to_type_dataplane(self, dataplane_yang_name):
        expected_yang = dataplane_yang_name
        expected_string = "dataplane"
        result = util.intf_name_to_type("dp0p1s1")
        assert expected_yang == result[0]
        assert expected_string == result[1].name

    def test_intf_name_to_type_unknown_type(self):
        with pytest.raises(ValueError):
            util.intf_name_to_type("dp0p")
