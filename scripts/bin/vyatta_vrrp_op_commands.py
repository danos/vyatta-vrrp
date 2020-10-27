#! /usr/bin/python3

# Copyright (c) 2020 AT&T Intellectual Property.
# All rights reserved.
#
# SPDX-License-Identifier: GPL-2.0-only

import argparse
from typing import Any, Dict, List

import vyatta.vrrp_vci.abstract_vrrp_classes as abstract_impl
import vyatta.vrrp_vci.keepalived.config_file as impl_conf
import vyatta.vrrp_vci.keepalived.dbus.process_control as process_control
import vyatta.vrrp_vci.keepalived.util as util
import vyatta.vrrp_vci.vyatta_vrrp_vci as vrrp_vci
from vyatta.vrrp_vci.vyatta_vrrp_vci import State


def bgp_async() -> None:
    keepalived_implementation: abstract_impl.ConfigFile \
        = impl_conf.KeepalivedConfig()
    current_state = State(keepalived_implementation)
    state_dict = util.sanitize_vrrp_config(current_state.get())
    intf_list: List
    for intf_list in state_dict[util.INTERFACE_YANG_NAME].values():
        intf_dict: Dict
        for intf_dict in intf_list:
            intf_name_key: str = util.get_namespace(
                intf_dict, util.YANG_INTERFACE_NAMESPACE
            )
            if intf_name_key == "":
                continue
            intf_name: str = intf_dict[intf_name_key]
            current_vrrp_namespace: str = util.get_namespace(
                intf_dict, util.VRRP_YANG_NAMESPACES
            )
            if current_vrrp_namespace == "":
                continue
            vrrp_instances: List = \
                intf_dict[current_vrrp_namespace][util.YANG_VRRP_GROUP]
            vrrp_instance: Dict
            for vrrp_instance in vrrp_instances:
                if util.YANG_INSTANCE_STATE not in vrrp_instance:
                    continue
                group: str = vrrp_instance[util.YANG_TAGNODE]
                state: Dict = vrrp_instance[util.YANG_INSTANCE_STATE]
                cmd = f"clear ip bgp interface {intf_name} vrrp-failover " +\
                    f"vrrp-group {group} state {state}"
                util.call_vtysh(cmd)


def process_arguments(command: str, intf: str, vrid: str) -> None:
    process = process_control.ProcessControl()
    if not process.is_running():
        print("VRRP not configured")
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
        process.turn_on_debugs(util.DEBUG_FLAG_PER_PACKET)
    elif command == "remove-debug":
        process.turn_off_debugs(util.DEBUG_FLAG_PER_PACKET)
    elif command == "garp":
        if intf == "" or vrid == "":
            return
        vrrp_vci.send_garp(
            {
                util.RPC_GARP_INTERFACE: intf,
                util.RPC_GARP_GROUP: vrid
            }
        )
    elif command == "bgp":
        bgp_async()
    return


def main() -> None:
    parser = argparse.ArgumentParser(description="Clear VRRP objects")
    parser.add_argument("clear",
                        help="Script to reload VRRP config or reset VRRP " +
                        "state\n",
                        choices=["reload", "reset", "add-debug",
                                 "remove-debug", "garp", "bgp"]
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
