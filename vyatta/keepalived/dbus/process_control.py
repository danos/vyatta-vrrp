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
from pathlib import Path
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
        self.systemd_default_file_path = "/etc/default/vyatta-keepalived"
        self.snmpd_conf_file_path = "/etc/snmp/snmpd.conf"

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

    def set_default_daemon_arguments(self) -> None:
        snmp_socket = self.get_agent_x_socket()  # type: str
        if snmp_socket != "":
            snmp_socket = "--snmp-agent-socket {}".format(snmp_socket)
        default_string = """# Options to pass to keepalived
# DAEMON_ARGS are appended to the keepalived command-line
DAEMON_ARGS="--snmp --log-facility=7 --log-detail --dump-conf -x --use-file /etc/keepalived/keepalived.conf --release-vips {}"
""".format(snmp_socket)  # noqa: E501  type: str
        with open(self.systemd_default_file_path, "w") as f_obj:
            f_obj.write(default_string)

    def get_agent_x_socket(self) -> str:
        snmp_socket = "tcp:localhost:705:1"  # type: str
        snmp_conf_file = Path(self.snmpd_conf_file_path)  # type: Path
        if (snmp_conf_file.exists() and snmp_conf_file.is_file()):
            with open(str(snmp_conf_file), "r") as f_obj:
                content = f_obj.readlines()
                content = [x.strip() for x in content]
                for line in content:
                    if "agentXSocket" in line:
                        snmp_socket = line.split(" ")[-1]
                        snmp_socket = "{}:1".format(snmp_socket)
                        break
        return snmp_socket

    def start_process(self) -> None:
        self.set_default_daemon_arguments()
        self.systemd_manager_intf.StartUnit(
            self.keepalived_service_file, "replace")

    def reload_process_config(self) -> None:
        self.systemd_manager_intf.ReloadUnit(
            self.keepalived_service_file, "replace")

    def restart_process(self) -> None:
        self.systemd_manager_intf.RestartUnit(
            self.keepalived_service_file, "replace")
