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
        conn = group_conn.VrrpConnection(
            "dp0p1s1", "1", "IPv4", sysbus
        )
        result = conn.get_instance_state()
        assert expected == result

    def test_get_unit_state_rfc(
            self, instance_state_rfc,
            mock_pydbus_rfc):
        import vyatta.keepalived.dbus.vrrp_group_connection \
            as group_conn
        import pydbus
        sysbus = pydbus.SystemBus()
        expected = instance_state_rfc
        conn = group_conn.VrrpConnection(
            "dp0p1s1", "1", "IPv4", sysbus
        )
        result = conn.get_instance_state()
        assert expected == result

    def test_garp(
            self, mock_pydbus):
        import vyatta.keepalived.dbus.vrrp_group_connection \
             as group_conn
        import pydbus
        sysbus = pydbus.SystemBus()
        expected = {}
        conn = group_conn.VrrpConnection(
            "dp0p1s1", "1", "IPv4", sysbus
        )
        result = conn.garp()
        assert expected == result
