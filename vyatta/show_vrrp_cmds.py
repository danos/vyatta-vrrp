#! /usr/bin/python3

# Copyright (c) 2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

from typing import Dict, List
import calendar
import time
import vyatta.keepalived.util as util


SHOW_SUMMARY_HEADER_LINE_1 = \
    ["", "", "", "RFC", "Addr", "Last", "Sync"]  # type: List
SHOW_SUMMARY_HEADER_LINE_2 = \
    ["Interface", "Group", "State", "Compliant", "Owner",
     "Transition", "Group"]  # type: List
SHOW_SUMMARY_HEADER_LINE_3 = \
    ["---------", "-----", "-----", "---------", "-----",
     "----------", "-----"]  # type: List
def show_summary_line_format(values: List[str]) -> str:
    return f"{values[0]:<18s}{values[1]:<7s}{values[2]:<8s}{values[3]:<11s}{values[4]:<7s}{values[5]:<12s}{values[6]}\n"

SHOW_DETAIL_DIVIDER = \
    "--------------------------------------------------\n"  # type: str
SHOW_DETAIL_INTF_DIVIDER = "--------------\n"  # type: str
def show_detail_intf_name(intf: str) -> str:
    return f"Interface: {intf}\n"
SHOW_DETAIL_GROUP_DIVIDER = "  ----------\n"  # type: str
def show_detail_group_name(group: str) -> str:
    return f"  Group: {group}\n"
def show_detail_line_format(line: List[str]) -> str:
    return f"  {line[0]:<30s}{line[1]:<s}\n"
def show_detail_tracked_format(line: List[str]) -> str:
    return f"    {line[0]}   state {line[1]}      {line[2]}\n"
def show_detail_tracked_pmon_format(line: List[str]) -> str:
    return f"      {line[0]}  {line[1]}  {line[2]}\n"

def show_sync_group_name(group: str) -> str:
    return f"Group: {group}\n"
SHOW_SYNC_GROUP_DIVIDER: str = SHOW_DETAIL_GROUP_DIVIDER[3:]
def show_sync_group_state_format(state: str) -> str:
    return f"  State: {state}\n  Monitoring:\n"
def show_sync_group_members_format(line: List[str]) -> str:
    return f"    Interface: {line[0]}, Group: {line[1]}\n"

def show_vrrp_summary(state_dict: Dict) -> str:
    output = "\n"  # type: str
    output += show_summary_line_format(SHOW_SUMMARY_HEADER_LINE_1)
    output += show_summary_line_format(SHOW_SUMMARY_HEADER_LINE_2)
    output += show_summary_line_format(SHOW_SUMMARY_HEADER_LINE_3)
    for intf_type in state_dict[util.INTERFACE_YANG_NAME]:
        intf_list = \
            state_dict[util.INTERFACE_YANG_NAME][intf_type]  # type: List
        for intf in intf_list:
            intf_name = intf[util.TAGNODE_YANG]
            vrrp_instances = intf[util.VRRP_YANG_NAME][util.VRRP_GROUP_YANG]
            for vrrp_instance in vrrp_instances:
                if util.INSTANCE_STATE_YANG not in vrrp_instance:
                    continue
                group = vrrp_instance[util.TAGNODE_YANG]
                state = vrrp_instance[util.INSTANCE_STATE_YANG]
                state_name = state["state"]
                if state['address-owner']:
                    ipao = "yes"
                else:
                    ipao = "no"
                if state["rfc-interface"] == "":
                    rfc = "no"
                else:
                    rfc = state["rfc-interface"]
                if state["sync-group"] == "":
                    sync = "<none>"
                else:
                    sync = state["sync-group"]
                now = calendar.timegm(time.localtime())
                last = state["last-transition"]
                diff = now - last
                output += \
                    show_summary_line_format(
                        [intf_name, group, state_name, rfc, ipao,
                        util.elapsed_time(diff), sync]
                    )
    return output + "\n"


def show_vrrp_detail(state_dict: Dict) -> str:
    output = "\n"  # type: str
    output += SHOW_DETAIL_DIVIDER
    for intf_type in state_dict[util.INTERFACE_YANG_NAME]:
        intf_list = \
            state_dict[util.INTERFACE_YANG_NAME][intf_type]  # type: List
        for intf in intf_list:
            intf_name = intf[util.TAGNODE_YANG]
            output += show_detail_intf_name(intf_name)
            output += SHOW_DETAIL_INTF_DIVIDER
            vrrp_instances = intf[util.VRRP_YANG_NAME][util.VRRP_GROUP_YANG]
            for vrrp_instance in vrrp_instances:
                if util.INSTANCE_STATE_YANG not in vrrp_instance:
                    continue
                group = vrrp_instance[util.TAGNODE_YANG]
                output += show_detail_group_name(group)
                output += SHOW_DETAIL_GROUP_DIVIDER
                state = vrrp_instance[util.INSTANCE_STATE_YANG]
                state_name = state["state"]
                output += show_detail_line_format(["State:", state_name])
                now = calendar.timegm(time.localtime())
                last = state["last-transition"]
                diff = now - last
                output += show_detail_line_format(
                    ["Last transition:", util.elapsed_time(diff)]
                )

                if state_name == "BACKUP":
                    output += "\n"
                    output += show_detail_line_format(
                        ["Master router:", state["master-router"]]
                    )
                    output += show_detail_line_format(
                        ["Master priority:", str(state["master-priority"])]
                    )

                output += "\n"
                version = state["version"]
                output += show_detail_line_format(
                    ["Version:", str(version)]
                )

                if state["rfc-interface"] != "":
                    output += show_detail_line_format(
                        ["RFC Compliant", ""]
                    )
                    output += show_detail_line_format(
                        ["Virtual MAC interface:", state["rfc-interface"]]
                    )
                if state["address-owner"]:
                    output += show_detail_line_format(
                        ["Address Owner:", "yes"]
                    )
                    output += "\n"
                elif state["rfc-interface"] != "":
                    output += show_detail_line_format(
                        ["Address Owner:", "no"]
                    )
                    output += "\n"
                    output += show_detail_line_format(
                        ["Source Address:", state["src-ip"]]
                    )

                output += show_detail_line_format(
                    ["Configured Priority:", str(state["base-priority"])]
                )
                output += show_detail_line_format(
                    ["Effective Priority:", str(state["effective-priority"])]
                )
                output += show_detail_line_format(
                    ["Advertisement interval:", state["advert-interval"]]
                )
                if version == 2:
                    auth_value = state["auth-type"]
                    if auth_value is None:
                        auth_value = "none"
                    output += show_detail_line_format(
                        ["Authentication type:", auth_value]
                    )

                preempt = "disabled"
                if state["preempt"]:
                    preempt = "enabled"
                output += show_detail_line_format(
                    ["Preempt:", preempt]
                )
                if "preempt-delay" in state:
                    output += show_detail_line_format(
                        ["Preempt delay:", state["preempt-delay"]]
                    )

                if "start-delay" in state:
                    output += show_detail_line_format(
                        ["Start delay:", state["start-delay"]]
                    )

                if version == 3:
                    accept = "disabled"
                    if state["accept"]:
                        accept = "enabled"
                    output += show_detail_line_format(
                        ["Accept:", accept]
                    )

                if state["sync-group"] != "":
                    output += "\n"
                    output += show_detail_line_format(
                        ["Sync-group:", "TEST"]
                    )

                output += "\n"
                if "track" in state:
                    track = state["track"]
                    if "interface" in track:
                        output += show_detail_line_format(
                            ["Tracked Interfaces count:",
                            str(len(track["interface"]))]
                        )
                        for intf in track["interface"]:
                            intf_weight = ""  # type: str
                            if "weight" in intf:
                                intf_weight = f"weight {intf['weight']}"
                            output += show_detail_tracked_format(
                                [intf["name"], intf["state"],
                                intf_weight]
                            )
                    if "monitor" in track:
                        output += show_detail_line_format(
                            ["Tracked Path Monitor count:",
                            str(len(track["monitor"]))]
                        )
                        for mont in track["monitor"]:
                            output += f"    {mont['name']}\n"
                            for pol in mont["policies"]:
                                policy_weight = ""  # type: str
                                if "weight" in pol:
                                    policy_weight = f"weight {pol['weight']}"
                                output += \
                                    show_detail_tracked_pmon_format(
                                        [pol["name"], pol["state"],
                                        policy_weight]
                                    )
                    if "route" in track:
                        output += show_detail_line_format(
                            ["Tracked routes count:",
                            str(len(track["route"]))]
                        )
                        for route in track["route"]:
                            route_weight = ""  # type: str
                            if "weight" in route:
                                route_weight = f"weight {route['weight']}"
                            output += show_detail_tracked_format(
                                [route["name"], route["state"],
                                route_weight]
                            )
                output += show_detail_line_format(
                    ["VIP count:", str(len(state["virtual-ips"]))]
                )
                for vip in state["virtual-ips"]:
                    output += f"    {vip}\n"
                output += "\n"
    return output


def show_vrrp_sync(state_dict: Dict) -> str:
    output: str = "\n"+SHOW_DETAIL_DIVIDER
    if (util.VRRP_YANG_NAME in state_dict):
        for sync_group in state_dict[util.VRRP_YANG_NAME]["sync-groups"]:
            output += show_sync_group_name(
                sync_group["name"]
            )
            output += SHOW_SYNC_GROUP_DIVIDER
            output += show_sync_group_state_format(
                sync_group["state"]
            )
            for group in sorted(sync_group["members"]):
                tokens: List[str] = group.split("-")
                output += show_sync_group_members_format(
                    tokens[1:]
                )
            output += "\n"
    return output
