#! /usr/bin/python3

# Copyright (c) 2020 AT&T Intellectual Property.
# All rights reserved.
#
# SPDX-License-Identifier: GPL-2.0-only

import argparse
from typing import Any, Dict

import vyatta.abstract_vrrp_classes as abstract_impl
import vyatta.keepalived.config_file as impl_conf
import vyatta.keepalived.dbus.process_control as process_control
import vyatta.keepalived.util as util


def process_arguments(command: str, intf: str, vrid: str) -> None:
    process = process_control.ProcessControl()
    if not process.is_running():
        return
    if command == "reload":
        process.reload_config()
    elif command == "reset":
        if intf == "" or vrid == "":
            return
        keepalived_implementation: abstract_impl.ConfigFile \
            = impl_conf.KeepalivedConfig()
        file_config: str = keepalived_implementation.read_config()
        yang_repr: Dict[str, Any] = \
            keepalived_implementation.convert_to_vci_format_dict(
                file_config)
        yang_repr = util.sanitize_vrrp_config(yang_repr)
        keepalived_implementation.update(yang_repr)
        instance_name = f"vyatta-{intf}-{vrid}"
        connections = keepalived_implementation.vrrp_connections
        connections[instance_name].reset_group_state()
    elif command == "add-debug":
        process.turn_on_debugs(util.PER_PACKET_DEBUG_FLAG)
    elif command == "remove-debug":
        process.turn_off_debugs(util.PER_PACKET_DEBUG_FLAG)
    return


def main() -> None:
    parser = argparse.ArgumentParser(description="Clear VRRP objects")
    parser.add_argument("clear",
                        help="Script to reload VRRP config or reset VRRP " +
                        "state\n",
                        choices=["reload", "reset", "add-debug",
                                 "remove-debug"]
                        )
    parser.add_argument(
        "--intf", help="Filter on interface", default=""
    )
    parser.add_argument(
        "--vrid", help="Filter on group", default=""
    )
    args = parser.parse_args()
    command: str = args.clear
    filter_intf: str = args.intf
    filter_vrid: str = args.vrid
    process_arguments(command, filter_intf, filter_vrid)
    return


if __name__ == "__main__":
    main()
