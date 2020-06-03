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
        assert actual == expected

    def test_get_hello_sources_no_hellos(
            self, simple_config):
        expected = []
        assert util.get_hello_sources(simple_config) == expected

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
    @pytest.mark.parametrize(
        "expected,address",
        [
            (True, "127.0.0.1"),
            (True, "::1"),
            (False, "10.1.1.1"),
        ],
        ids=[
            "ipv4", "ipv6", "No configured"
        ]
    )
    def test_is_local_address(self, expected, address):
        assert util.is_local_address(address) == expected

    @pytest.mark.sanity
    @pytest.mark.parametrize(
        "expected,config",
        [
            (
                False,
                pytest.lazy_fixture("simple_config")
            ),
            (
                True,
                pytest.lazy_fixture("complex_config")
            ),
        ],
        ids=[
            "no", "yes"
        ]
    )
    def test_is_rfc_compat_configured(
            self, expected, config):
        assert util.is_rfc_compat_configured(config) == expected

    @pytest.mark.parametrize(
        "expected,hypervisor",
        [
            (False,
             pytest.lazy_fixture("mock_show_version_rpc_no_hypervisor")),
            (False, pytest.lazy_fixture("mock_show_version_rpc_kvm")),
            (True, pytest.lazy_fixture("mock_show_version_rpc_vmware")),
        ],
        ids=[
            "Baremetal", "KVM", "VMWare"
        ]
    )
    def test_running_on_vmware(
            self, expected, hypervisor):
        assert util.running_on_vmware() == expected

    @pytest.mark.sanity
    def test_sanitize_vrrp_config_one_configured(self,
                                                 simple_config):
        assert util.sanitize_vrrp_config(simple_config) == simple_config
        assert util.sanitize_vrrp_config(simple_config) is not simple_config

    @pytest.mark.parametrize(
        "test_value,expected_value",
        [
            (pytest.lazy_fixture("no_vrrp_config"),
             pytest.lazy_fixture("top_level_dictionary")),
            (pytest.lazy_fixture("simple_multi_intf_same_type_config"),
             pytest.lazy_fixture("simple_config")),
            (pytest.lazy_fixture("simple_multi_intf_differing_type_config"),
             pytest.lazy_fixture(
                 "simple_multi_intf_differing_type_config_sanitized")
             ),
            (pytest.lazy_fixture("simple_dataplane_vif_config"),
             pytest.lazy_fixture("simple_config")),
            (pytest.lazy_fixture("simple_dataplane_vif_with_vrrp_config"),
             pytest.lazy_fixture("simple_dataplane_vif_sanitized_config")),
            (pytest.lazy_fixture("simple_multi_intf_type_vif_config"),
             pytest.lazy_fixture(
                 "simple_multi_intf_type_vif_sanitized_config")
             ),
        ],
        ids=[
            "No configured groups",
            "Two interfaces, one with and one without config",
            "Two types of interface with VRRP config",
            "Parent with config, vif without",
            "Move vif dataplane",
            "Move bonding and dataplane vif"
        ]
    )
    def test_sanitize_vrrp_config(
            self, test_value, expected_value):
        assert test_value != expected_value
        assert util.sanitize_vrrp_config(test_value) == expected_value

    @pytest.mark.parametrize(
        "file_contents,search_string,expected",
        [
            (
                pytest.lazy_fixture("autogeneration_string"),
                "global_defs",
                [6]
            ),
            (
                pytest.lazy_fixture("autogeneration_string"),
                "vrrp_instance",
                []
            ),
            (
                pytest.lazy_fixture("simple_keepalived_config"),
                "vrrp_instance",
                [13]
            ),
            (
                pytest.lazy_fixture("multiple_group_keepalived_config"),
                "vrrp_instance",
                [13, 25]
            ),
        ],
        ids=[
            "Global defs", "No instances", "Single instance",
            "Multiple instances"
        ]
    )
    def test_get_config_indexes_list_autogen(
            self, file_contents, search_string, expected):
        result = util.get_config_indexes(
            file_contents.splitlines(), search_string)
        assert result == expected

    @pytest.mark.parametrize(
        "config_string,start_index,expected_block",
        [
            (
                pytest.lazy_fixture("autogeneration_string"),
                [6],
                pytest.lazy_fixture("autogeneration_config_block"),
            ),
            (
                pytest.lazy_fixture("autogeneration_string"),
                [],
                [],
            ),
            (
                pytest.lazy_fixture("simple_keepalived_config"),
                [13],
                pytest.lazy_fixture("simple_keepalived_config_block"),
            ),
            (
                pytest.lazy_fixture("multiple_group_keepalived_config"),
                [13, 25],
                pytest.lazy_fixture("multiple_group_keepalived_config_block"),
            ),
        ],
        ids=[
            "Global defs", "No instances", "One instance",
            "Multiple instances"
        ]
    )
    def test_get_config_blocks(
            self, config_string, start_index, expected_block):
        assert util.get_config_blocks(
            config_string.splitlines(), start_index
        ) == expected_block

    @pytest.mark.parametrize(
        "config_list,search_string,expected",
        [
            (
                pytest.lazy_fixture("autogeneration_config_block"),
                "snmp_socket",
                {"Name": "CONFIGURED", "Value": "tcp:localhost:705:1"},
            ),
            (
                pytest.lazy_fixture("autogeneration_config_block"),
                "garp",
                {"Name": "MISSING", "Value": "NOTFOUND"},
            ),
            (
                pytest.lazy_fixture("autogeneration_config_block"),
                "enable_dbus",
                {"Name": "PRESENT", "Value": [None]},
            ),
            (
                pytest.lazy_fixture("complex_keepalived_config_block"),
                "preempt",
                {"Name": "MISSING", "Value": "NOTFOUND"},
            ),
            (
                pytest.lazy_fixture("multiple_group_keepalived_config_block"),
                "state",
                {"Name": "CONFIGURED", "Value": "BACKUP"},
            ),
        ],
        ids=[
            "Autogen SNMP defined", "Autogen undefined key",
            "Autogen presence defined", "Overlapping substring",
            "Multiple config blocks"
        ]
    )
    def test_find_value_in_config_blocks(
            self, config_list, search_string, expected):
        for block in config_list:
            assert util.find_config_value(block, search_string).name \
                == expected["Name"]
            assert util.find_config_value(block, search_string).value \
                == expected["Value"]

    @pytest.mark.parametrize(
        "intf_name,intf_list,intf_index",
        [
            (
                "dp0p1s1",
                pytest.lazy_fixture("search_empty_dataplane_list"),
                0
            ),
            (
                "dp0p1s1",
                pytest.lazy_fixture("search_dataplane_list"),
                0
            ),
            (
                "dp0p1s2",
                pytest.lazy_fixture("search_dataplane_list"),
                1
            ),
        ],
        ids=[
            "Empty interface list", "Group in interface list",
            "Group not in interface list"
        ]
    )
    def test_find_interface_in_yang(
            self, intf_name, intf_list, intf_index):
        assert util.find_interface_in_yang_repr(
            intf_name, "", intf_list) in intf_list
        assert util.find_interface_in_yang_repr(
            intf_name, "", intf_list) is intf_list[intf_index]

    @pytest.mark.parametrize(
        "intf_name,vif_number,intf_list,intf_index,vif_index",
        [
            (
                "dp0p1s1",
                "10",
                pytest.lazy_fixture("search_empty_dataplane_list"),
                0, 0
            ),
            (
                "dp0p1s1",
                "10",
                pytest.lazy_fixture("search_dataplane_list"),
                0, 0
            ),
            (
                "dp0p1s1",
                "20",
                pytest.lazy_fixture("search_vif_dataplane_list"),
                0, 1
            ),
            (
                "dp0p1s1",
                "10",
                pytest.lazy_fixture(
                    "search_vif_dataplane_list_multiple_vrrp_groups"
                ),
                0, 0
            ),
        ],
        ids=[
            "interface doesnt exist, vif doesn't exist",
            "interface exists, vif doesn't exist",
            "interface exists, multiple vifs exist",
            "interface exists, vif exists with multiple VRRP groups"
        ]
    )
    def test_find_interface_in_yang_for_vifs(
            self, intf_name, vif_number, intf_list, intf_index, vif_index):
        assert util.find_interface_in_yang_repr(
            intf_name, vif_number, intf_list) in intf_list[intf_index]["vif"]
        assert util.find_interface_in_yang_repr(
            intf_name, vif_number, intf_list) is \
            intf_list[intf_index]["vif"][vif_index]

    @pytest.mark.parametrize(
        "intf_name,yang_name,common_name",
        [
            (
                "dp0bond1",
                pytest.lazy_fixture("bonding_yang_name"),
                "bonding"
            ),
            (
                "sw0",
                pytest.lazy_fixture("switch_yang_name"),
                "switch"
            ),
            (
                "dp0p1s1",
                pytest.lazy_fixture("dataplane_yang_name"),
                "dataplane"
            ),
        ],
        ids=[
            "Bonding", "switch", "dataplane"
        ]
    )
    def test_intf_name_to_type(self, intf_name, yang_name, common_name):
        assert util.intf_name_to_type(intf_name)[0] == yang_name
        assert util.intf_name_to_type(intf_name)[1].name == common_name

    def test_intf_name_to_type_unknown_type(self):
        with pytest.raises(ValueError):
            util.intf_name_to_type("dp0p")
