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
import time
from functools import wraps
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import pydbus

import vyatta.keepalived.util as util


def get_vrrp_proxy(func) -> Callable:
    @wraps(func)
    def wrapper(inst: 'ProcessControl', *args, **kwargs) -> Callable:
        if inst.vrrp_proxy_process is None:
            inst.vrrp_proxy_process = inst.sysbus.get(
                util.KEEPALIVED_DBUS_INTF_NAME,
                util.VRRP_PROCESS_DBUS_INTF_PATH
            )
        return func(inst, *args, **kwargs)
    return wrapper


class ProcessControl:

    def __init__(self) -> None:
        """
        This object models controlling the parent Keepalived process using DBus
        and systemd commands.
        """

        self.keepalived_service_file: str = "keepalived.service"

        self.log: logging.Logger = logging.getLogger("vyatta-vrrp-vci")
        self.sysbus: pydbus.Bus = pydbus.SystemBus()

        self.systemd_proxy: pydbus.ProxyObject = self.sysbus.get(
            util.SYSTEMD_DBUS_INTF_NAME,
            util.SYSTEMD_DBUS_PATH
        )

        self.systemd_manager_intf: pydbus.interface = self.systemd_proxy[
            util.SYSTEMD_MANAGER_DBUS_INTF_NAME
        ]
        self.keepalived_unit_file_intf: pydbus.ProxyMethod = \
            self.systemd_proxy.LoadUnit(
                self.keepalived_service_file
            )

        self.keepalived_proxy_obj: pydbus.ProxyObject = \
            self.sysbus.get(
                util.SYSTEMD_DBUS_INTF_NAME,
                self.keepalived_unit_file_intf
            )
        self.vrrp_proxy_process: pydbus.ProxyObject = None
        self.running_state: str = "UNKNOWN"
        self.systemd_default_file_path: str = "/etc/default/keepalived"
        self.snmpd_conf_file_path: str = "/etc/snmp/snmpd.conf"

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
        """
        Generate the default commands that Keepalived is passed on start up
        """

        snmp_socket: str = self.get_agent_x_socket()
        if snmp_socket != "":
            snmp_socket = f"--snmp-agent-socket {snmp_socket}"
        default_string: str = f"""# Options to pass to keepalived
# DAEMON_ARGS are appended to the keepalived command-line
DAEMON_ARGS="--snmp --log-facility=7 --log-detail --dump-conf -x --use-file /etc/keepalived/keepalived.conf --release-vips {snmp_socket}"
"""  # noqa: E501
        with open(self.systemd_default_file_path, "w") as f_obj:
            f_obj.write(default_string)

    def get_agent_x_socket(self) -> str:
        """
        Find how we should connect to the SNMP AgentX protocol.
        This can be changed but it is usually 'tcp:localhost:705:1'
        The 1 at the end of the connection string is the Global VRF, this is
        required so Keepalived connects to AgentX correctly.
        """

        snmp_socket: str = "tcp:localhost:705:1"
        snmp_conf_file: Path = Path(self.snmpd_conf_file_path)
        if (snmp_conf_file.exists() and snmp_conf_file.is_file()):
            with open(str(snmp_conf_file), "r") as f_obj:
                content: List[str] = f_obj.readlines()
                content = [x.strip() for x in content]
                for line in content:
                    if "agentXSocket" in line:
                        snmp_socket = line.split(" ")[-1]
                        snmp_socket = f"{snmp_socket}:1"
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

    @get_vrrp_proxy
    def get_rfc_mapping(self, intf: str) -> Dict[str, str]:
        """
        Given an RFC interface return the receiving interface and group that
        relate to that RFC interface. Used in RPC calls.
        """

        if not self.is_running():
            return {
                f"{util.VRRP_NAMESPACE}:receive": "",
                f"{util.VRRP_NAMESPACE}:group": 0
            }
        rfc_mapping: Tuple[str, str] = \
            self.vrrp_proxy_process.GetRfcMapping(intf)
        return {
            f"{util.VRRP_NAMESPACE}:receive":
            rfc_mapping[0],
            f"{util.VRRP_NAMESPACE}:group":
            rfc_mapping[1]}

    def subscribe_process_signals(self) -> None:
        self.log.debug("Keepalived instance subscribing to signals")

    @get_vrrp_proxy
    def dump_keepalived_data(self) -> bool:
        """
        Signal keepalived to write it's running data file.
        We wait up to 3 seconds for it to be written, if the file isn't
        written in this time keepalived isn't responding.
        """

        if not self.is_running():
            return
        data_file = Path(util.KEEPALIVED_DATA_FILE_PATH)
        if data_file.exists():
            data_file.unlink()
        self.vrrp_proxy_process.PrintData()
        data_file = Path(util.KEEPALIVED_DATA_FILE_PATH)
        wait_for_write: int = 0
        while wait_for_write < 3:
            if data_file.exists():
                break
            time.sleep(1)
            wait_for_write += 1
        return data_file.exists()

    @get_vrrp_proxy
    def dump_keepalived_stats(self) -> bool:
        """
        Signal keepalived to write it's running stats file.
        We wait up to 3 seconds for it to be written, if the file isn't
        written in this time keepalived isn't responding.
        """

        if not self.is_running():
            return
        stats_file = Path(util.KEEPALIVED_STATS_FILE_PATH)
        if stats_file.exists():
            stats_file.unlink()
        self.vrrp_proxy_process.PrintStats()
        stats_file = Path(util.KEEPALIVED_STATS_FILE_PATH)
        wait_for_write: int = 0
        while wait_for_write < 3:
            if stats_file.exists():
                break
            time.sleep(1)
            wait_for_write += 1
        return stats_file.exists()

    @get_vrrp_proxy
    def reload_config(self) -> None:
        """
        Separate from the systemd config reload above, this function
        uses the keepalived DBus interface to re-read the processes'
        config file.
        """
        if not self.is_running():
            return
        self.vrrp_proxy_process.ReloadConfig()

    @get_vrrp_proxy
    def turn_on_debugs(self, debug_value: int) -> None:
        if not self.is_running():
            return
        self.vrrp_proxy_process.AddDebug(debug_value)

    @get_vrrp_proxy
    def turn_off_debugs(self, debug_value: int) -> None:
        if not self.is_running():
            return
        self.vrrp_proxy_process.RemoveDebug(debug_value)
