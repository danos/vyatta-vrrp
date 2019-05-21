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
import dbus


class ProcessControl:

    def __init__(self):
        self.systemd_obj_name = "org.freedesktop.systemd1"
        systemd_obj_path = "/org/freedesktop/systemd1"
        self.keepalived_service_file = "vyatta-keepalived.service"

        self.log = logging.getLogger("vyatta-vrrp-vci")
        self.sysbus = dbus.SystemBus()

        self.systemd_proxy = self.sysbus.get_object(
            self.systemd_obj_name, systemd_obj_path
        )

        self.systemd_manager_intf_name = \
            "{}.Manager".format(self.systemd_obj_name)
        self.systemd_manager_intf = \
            dbus.Interface(
                self.systemd_proxy,
                dbus_interface=self.systemd_manager_intf_name
            )
        self.keepalived_unit_file_intf = \
            self.systemd_manager_intf.LoadUnit(
                self.keepalived_service_file
            )

        self.keepalived_proxy_obj = \
            self.sysbus.get_object(
                self.systemd_obj_name,
                str(self.keepalived_unit_file_intf)
            )
        self.running_state = "UNKNOWN"

    def unit_state(self):
        return self.running_state

    def refresh_unit_state(self):
        self.running_state = \
            self.keepalived_proxy_obj.Get(
                "org.freedesktop.systemd1.Unit",
                "SubState",
                dbus_interface="org.freedesktop.DBus.Properties"
            )

    def is_running(self):
        self.refresh_unit_state()
        if self.running_state == "running":
            return True
        return False

    def shutdown_process(self):
        self.systemd_manager_intf.StopUnit(
            self.keepalived_service_file, "replace")

    def restart_process(self):
        self.systemd_manager_intf.RestartUnit(
            self.keepalived_service_file, "replace")
