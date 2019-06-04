#! /usr/bin/python3


import pytest  # noqa: F401


class TestKeepalivedVrrpGroupControl:

    def test_get_unit_state(
            self, mock_pydbus, instance_state):
        import vyatta.keepalived.dbus.vrrp_group_connection \
            as group_conn
        import pydbus
        sysbus = pydbus.SystemBus()
        expected = instance_state
        result = group_conn.get_instance_state(
            "dp0p1s1", "1", "IPv4", sysbus
        )
        assert expected == result

    def test_get_unit_state_rfc(
            self, instance_state_rfc,
            mock_pydbus_rfc):
        import vyatta.keepalived.dbus.vrrp_group_connection \
            as group_conn
        import pydbus
        sysbus = pydbus.SystemBus()
        expected = instance_state_rfc
        result = group_conn.get_instance_state(
            "dp0p1s1", "1", "IPv4", sysbus
        )
        assert expected == result

    def test_garp(
            self, mock_pydbus):
        import vyatta.keepalived.dbus.vrrp_group_connection \
             as group_conn
        import pydbus
        sysbus = pydbus.SystemBus()
        expected = {}
        result = group_conn.garp("dp0p1s1", "1", sysbus)
        assert expected == result

    def test_find_recv_intf_no_rfc(
            self, mock_pydbus):
        import vyatta.keepalived.dbus.vrrp_group_connection \
             as group_conn
        import pydbus
        sysbus = pydbus.SystemBus()
        expected = {"vyatta-vrrp-v1:receive": "",
                    "vyatta-vrrp-v1:group": 0}
        result = group_conn.get_rfc_mapping("dp0p1s1", sysbus)
        assert expected == result

    def test_find_recv_intf_rfc(
            self, mock_pydbus):
        import vyatta.keepalived.dbus.vrrp_group_connection \
             as group_conn
        import pydbus
        sysbus = pydbus.SystemBus()
        expected = {"vyatta-vrrp-v1:receive": "dp0p1s1",
                    "vyatta-vrrp-v1:group": 1}
        result = group_conn.get_rfc_mapping("dp0vrrp1", sysbus)
        assert expected == result
