# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only.

import pytest

import vyatta.vrrp_vci.keepalived.util as util


class TestKeepalivedVrrpGroupControl:

    @pytest.mark.parametrize(
        "expected,fakes",
        [
            (pytest.lazy_fixture("instance_state"),
             pytest.lazy_fixture("mock_pydbus")),
            (pytest.lazy_fixture("instance_state_rfc"),
             pytest.lazy_fixture("mock_pydbus_rfc"))
        ],
        ids=["Non rfc", "rfc"])
    def test_get_unit_state(self, expected, fakes):
        import vyatta.vrrp_vci.keepalived.dbus.vrrp_group_connection \
            as group_conn
        import pydbus
        sysbus = pydbus.SystemBus()
        conn = group_conn.VrrpConnection(
            "dp0p1s1", "1", 4, sysbus
        )
        util.VRRP_INSTANCE_DBUS_INTF_NAME = "dp0p1s1"

        assert conn.get_instance_state() == expected

    def test_garp(self, mock_pydbus):
        import vyatta.vrrp_vci.keepalived.dbus.vrrp_group_connection \
            as group_conn
        import pydbus

        sysbus = pydbus.SystemBus()
        conn = group_conn.VrrpConnection("dp0p1s1", "1", 4, sysbus)

        assert conn.garp() is None

    def test_vif_sanitizing(
            self, mock_pydbus):
        import vyatta.vrrp_vci.keepalived.dbus.vrrp_group_connection \
            as group_conn
        import pydbus

        sysbus = pydbus.SystemBus()
        conn = group_conn.VrrpConnection("dp0p1s1.10", "1", 4, sysbus)

        expected = "/org/keepalived/Vrrp1/Instance/dp0p1s1_10/1/IPv4"
        assert conn.dbus_path == expected
