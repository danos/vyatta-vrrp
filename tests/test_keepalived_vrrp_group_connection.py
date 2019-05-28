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
            self, mock_pydbus_rfc, instance_state_rfc):
        import vyatta.keepalived.dbus.vrrp_group_connection \
            as group_conn
        import pydbus
        sysbus = pydbus.SystemBus()
        expected = instance_state_rfc
        result = group_conn.get_instance_state(
            "dp0p1s1", "1", "IPv4", sysbus
        )
        assert expected == result
