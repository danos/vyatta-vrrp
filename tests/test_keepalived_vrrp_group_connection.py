#! /usr/bin/python3


import pytest  # noqa: F401

import vyatta.keepalived.util as util


class TestKeepalivedVrrpGroupControl:

    def test_get_unit_state(
            self, mock_pydbus, instance_state):
        import vyatta.keepalived.dbus.vrrp_group_connection \
            as group_conn
        import pydbus
        sysbus = pydbus.SystemBus()
        expected = instance_state
        conn = group_conn.VrrpConnection(
            "dp0p1s1", "1", 4, sysbus
        )
        util.VRRP_INSTANCE_DBUS_INTF_NAME = "dp0p1s1"
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
            "dp0p1s1", "1", 4, sysbus
        )
        util.VRRP_INSTANCE_DBUS_INTF_NAME = "dp0p1s1"
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
            "dp0p1s1", "1", 4, sysbus
        )
        result = conn.garp()
        assert expected == result

    def test_vif_sanitizing(
            self, mock_pydbus):
        import vyatta.keepalived.dbus.vrrp_group_connection \
            as group_conn
        import pydbus
        sysbus = pydbus.SystemBus()
        expected = \
            f"/org/keepalived/Vrrp1/Instance/dp0p1s1_10/1/IPv4"
        conn = group_conn.VrrpConnection(
            "dp0p1s1.10", "1", 4, sysbus
        )
        result = conn.dbus_path
        assert expected == result
