#! /usr/bin/python3

# Copyright (c) 2020 AT&T Intellectual Property.
# All rights reserved.
#
# SPDX-License-Identifier: GPL-2.0-only

import argparse
from typing import Dict

import vci
import vyatta.show_vrrp_cmds as vrrp_show
from vyatta.vyatta_vrrp_vci import State
import vyatta.keepalived.config_file as impl_conf
import vyatta.keepalived.util as util
import vyatta.keepalived.dbus.process_control as process_control
import vyatta.abstract_vrrp_classes as abstract_impl


def process_arguments(command: str, intf: str, vrid: str, sync: str) -> str:
    show_output: str = "VRRP is not running"
    if command == "summary":
        keepalived_implementation: abstract_impl.ConfigFile \
            = impl_conf.KeepalivedConfig()
        current_state = State(keepalived_implementation)
        state_dict = current_state.get()
        if state_dict == {}:
            return show_output
        show_output = vrrp_show.show_vrrp_summary(current_state.get())
    else:
        pc = process_control.ProcessControl()
        if not pc.is_running():
            return show_output
        file_contents: str
        json_repr: Dict
        if command == "detail" or command == "interface" or command == "sync":
            keepalived_responding = pc.dump_keepalived_data()
            if not keepalived_responding:
                return "Keepalived is not responding"
            with open(util.KEEPALIVED_DATA_FILE_PATH, "r") as file_obj:
                file_contents = file_obj.read()
            json_repr = vrrp_show.convert_data_file_to_dict(file_contents)
            if command == "detail":
                show_output = vrrp_show.show_vrrp_detail(json_repr)
            elif command == "interface":
                show_output = vrrp_show.show_vrrp_interface(json_repr, intf, vrid)
            elif command == "sync":
                show_output = vrrp_show.show_vrrp_sync(json_repr, sync)
            else:
                print("Something has gone horribly wrong")
        else:
            keepalived_responding = pc.dump_keepalived_stats()
            if not keepalived_responding:
                return "Keepalived is not responding"
            with open(util.KEEPALIVED_STATS_FILE_PATH, "r") as file_obj:
                file_contents = file_obj.read()
            json_repr= vrrp_show.convert_stats_file_to_dict(file_contents)
            show_output = vrrp_show.show_vrrp_statistics_filters(
                json_repr, intf, vrid
            )
    return show_output


def main() -> str:
    parser = argparse.ArgumentParser(description="Show output for VRRP")
    parser.add_argument("show" , 
        help="""The show command to display\n
        summary - show vrrp\n
        detail - show vrrp detail\n
        interface - show vrrp interface\n
        stats - show vrrp statistics\n
        sync - show vrrp sync-group\n
        """,
        choices=["summary", "detail", "interface", "stats", "sync"]
    )
    parser.add_argument(
        "--intf", help="Filter on interface", default=""
    )
    parser.add_argument(
        "--vrid", help="Filter on group", default=""
    )
    parser.add_argument(
        "--sync", help="Filter sync group", default=""
    )
    args = parser.parse_args()
    command: str = args.show
    filter_intf: str = args.intf
    filter_vrid: str = args.vrid
    filter_sync: str = args.sync
    return process_arguments(command, filter_intf, filter_vrid, filter_sync)


if __name__ == "__main__":
    main()
