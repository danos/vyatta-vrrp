#! /ust/bin/env python3

"""
Vyatta VCI component to configure keepalived to provide VRRP functionality
This file provides functionality for starting and stopping the keepalived
process using dbus controls.
"""

# Copyright (c) 2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only


import logging
import pydbus
import vyatta.keepalived.util as util


class ProcessControl:

    def __init__(self):
        self.keepalived_service_file = "vyatta-keepalived.service"

        self.log = logging.getLogger("vyatta-vrrp-vci")
        self.sysbus = pydbus.SystemBus()

        self.systemd_proxy = self.sysbus.get(
            util.SYSTEMD_DBUS_INTF_NAME,
            util.SYSTEMD_DBUS_PATH
        )

        self.systemd_manager_intf = \
            self.systemd_proxy[util.SYSTEMD_MANAGER_DBUS_INTF_NAME]
        self.keepalived_unit_file_intf = \
            self.systemd_proxy.LoadUnit(
                self.keepalived_service_file
            )

        self.keepalived_proxy_obj = \
            self.sysbus.get(
                util.SYSTEMD_DBUS_INTF_NAME,
                self.keepalived_unit_file_intf
            )
        self.running_state = "UNKNOWN"

    def unit_state(self) -> str:
        return self.running_state

    def refresh_unit_state(self) -> None:
        self.running_state = \
            self.keepalived_proxy_obj.SubState

    def is_running(self) -> bool:
        self.refresh_unit_state()
        if self.running_state == "running":
            return True
        return False

    def shutdown_process(self) -> None:
        self.systemd_manager_intf.StopUnit(
            self.keepalived_service_file, "replace")

    def start_process(self) -> None:
        self.systemd_manager_intf.StartUnit(
            self.keepalived_service_file, "replace")

    def reload_process_config(self) -> None:
        self.systemd_manager_intf.ReloadUnit(
            self.keepalived_service_file, "replace")

    def restart_process(self) -> None:
        self.systemd_manager_intf.RestartUnit(
            self.keepalived_service_file, "replace")
