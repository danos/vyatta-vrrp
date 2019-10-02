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
SHOW_SUMMARY_LINE_FORMAT = \
    "{0:<18s}{1:<7s}{2:<8s}{3:<11s}{4:<7s}{5:<12s}{6}\n"  # type: str

SHOW_DETAIL_DIVIDER = \
    "--------------------------------------------------\n"  # type: str
SHOW_DETAIL_INTF_DIVIDER = "--------------\n"  # type: str
SHOW_DETAIL_INTF_NAME = "Interface: {}\n"  # type: str
SHOW_DETAIL_GROUP_DIVIDER = "  ----------\n"  # type: str
SHOW_DETAIL_GROUP_NAME = "  Group: {}\n"  # type: str
SHOW_DETAIL_LINE_FORMAT = \
    "  {0:<30s}{1:<s}\n"  # type: str
SHOW_DETAIL_TRACKED_FORMAT = \
    "    {0}   state {1}      {2}\n"  # type: str
SHOW_DETAIL_TRACKED_PMON_FORMAT = \
    "      {0}  {1}  {2}\n"  # type: str


def show_vrrp_summary(state_dict: Dict) -> str:
    output = "\n"  # type: str
    output += SHOW_SUMMARY_LINE_FORMAT.format(
        *SHOW_SUMMARY_HEADER_LINE_1
    )
    output += SHOW_SUMMARY_LINE_FORMAT.format(
        *SHOW_SUMMARY_HEADER_LINE_2
    )
    output += SHOW_SUMMARY_LINE_FORMAT.format(
        *SHOW_SUMMARY_HEADER_LINE_3
    )
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
                    SHOW_SUMMARY_LINE_FORMAT.format(
                        intf_name, group, state_name, rfc, ipao,
                        util.elapsed_time(diff), sync
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
            output += SHOW_DETAIL_INTF_NAME.format(intf_name)
            output += SHOW_DETAIL_INTF_DIVIDER
            vrrp_instances = intf[util.VRRP_YANG_NAME][util.VRRP_GROUP_YANG]
            for vrrp_instance in vrrp_instances:
                if util.INSTANCE_STATE_YANG not in vrrp_instance:
                    continue
                group = vrrp_instance[util.TAGNODE_YANG]
                output += SHOW_DETAIL_GROUP_NAME.format(group)
                output += SHOW_DETAIL_GROUP_DIVIDER
                state = vrrp_instance[util.INSTANCE_STATE_YANG]
                state_name = state["state"]
                output += SHOW_DETAIL_LINE_FORMAT.format("State:", state_name)
                now = calendar.timegm(time.localtime())
                last = state["last-transition"]
                diff = now - last
                output += SHOW_DETAIL_LINE_FORMAT.format(
                    "Last transition:", util.elapsed_time(diff)
                )

                if state_name == "BACKUP":
                    output += "\n"
                    output += SHOW_DETAIL_LINE_FORMAT.format(
                        "Master router:", state["master-router"]
                    )
                    output += SHOW_DETAIL_LINE_FORMAT.format(
                        "Master priority:", str(state["master-priority"])
                    )

                output += "\n"
                version = state["version"]
                output += SHOW_DETAIL_LINE_FORMAT.format(
                    "Version:", str(version)
                )

                if state["rfc-interface"] != "":
                    output += SHOW_DETAIL_LINE_FORMAT.format(
                        "RFC Compliant", ""
                    )
                    output += SHOW_DETAIL_LINE_FORMAT.format(
                        "Virtual MAC interface:", state["rfc-interface"]
                    )
                if state["address-owner"]:
                    output += SHOW_DETAIL_LINE_FORMAT.format(
                        "Address Owner:", "yes"
                    )
                    output += "\n"
                elif state["rfc-interface"] != "":
                    output += SHOW_DETAIL_LINE_FORMAT.format(
                        "Address Owner:", "no"
                    )
                    output += "\n"
                    output += SHOW_DETAIL_LINE_FORMAT.format(
                        "Source Address:", state["src-ip"]
                    )

                output += SHOW_DETAIL_LINE_FORMAT.format(
                    "Configured Priority:", str(state["base-priority"])
                )
                output += SHOW_DETAIL_LINE_FORMAT.format(
                    "Effective Priority:", str(state["effective-priority"])
                )
                output += SHOW_DETAIL_LINE_FORMAT.format(
                    "Advertisement interval:", state["advert-interval"]
                )
                if version == 2:
                    auth_value = state["auth-type"]
                    if auth_value is None:
                        auth_value = "none"
                    output += SHOW_DETAIL_LINE_FORMAT.format(
                        "Authentication type:", auth_value
                    )

                preempt = "disabled"
                if state["preempt"]:
                    preempt = "enabled"
                output += SHOW_DETAIL_LINE_FORMAT.format(
                    "Preempt:", preempt
                )

                if version == 3:
                    accept = "disabled"
                    if state["accept"]:
                        accept = "enabled"
                    output += SHOW_DETAIL_LINE_FORMAT.format(
                        "Accept:", accept
                    )

                if state["sync-group"] != "":
                    output += "\n"
                    output += SHOW_DETAIL_LINE_FORMAT.format(
                        "Sync-group:", "TEST"
                    )

                output += "\n"
                if "track" in state:
                    track = state["track"]
                    if "interface" in track:
                        output += SHOW_DETAIL_LINE_FORMAT.format(
                            "Tracked Interfaces count:",
                            str(len(track["interface"]))
                        )
                        for intf in track["interface"]:
                            intf_weight = ""  # type: str
                            if "weight" in intf:
                                intf_weight = "weight {}".format(
                                    intf["weight"]
                                )
                            output += SHOW_DETAIL_TRACKED_FORMAT.format(
                                intf["name"], intf["state"],
                                intf_weight
                            )
                    if "monitor" in track:
                        output += SHOW_DETAIL_LINE_FORMAT.format(
                            "Tracked Path Monitor count:",
                            str(len(track["monitor"]))
                        )
                        for mont in track["monitor"]:
                            output += "    {}\n".format(mont["name"])
                            for pol in mont["policies"]:
                                policy_weight = ""  # type: str
                                if "weight" in pol:
                                    policy_weight = "weight {}".format(
                                        pol["weight"]
                                    )
                                output += \
                                    SHOW_DETAIL_TRACKED_PMON_FORMAT.format(
                                        pol["name"], pol["state"],
                                        policy_weight
                                    )
                    if "route" in track:
                        output += SHOW_DETAIL_LINE_FORMAT.format(
                            "Tracked routes count:",
                            str(len(track["route"]))
                        )
                        for route in track["route"]:
                            route_weight = ""  # type: str
                            if "weight" in route:
                                route_weight = "weight {}".format(
                                    route["weight"]
                                )
                            output += SHOW_DETAIL_TRACKED_FORMAT.format(
                                route["name"], route["state"],
                                route_weight
                            )
                output += SHOW_DETAIL_LINE_FORMAT.format(
                    "VIP count:", str(len(state["virtual-ips"]))
                )
                for vip in state["virtual-ips"]:
                    output += "    {}\n".format(vip)
                output += "\n"
    return output
