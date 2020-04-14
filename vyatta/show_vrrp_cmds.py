#! /usr/bin/python3

# Copyright (c) 2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

from typing import Dict, List, Tuple, Union, Optional, Any
import calendar
import time

import vyatta.keepalived.util as util

""" Show vrrp summary helpers """
SHOW_SUMMARY_HEADER_LINE_1: List[str] = \
    ["", "", "", "RFC", "Addr", "Last", "Sync"]
SHOW_SUMMARY_HEADER_LINE_2: List[str] = \
    ["Interface", "Group", "State", "Compliant", "Owner",
     "Transition", "Group"]
SHOW_SUMMARY_HEADER_LINE_3: List[str] = \
    ["---------", "-----", "-----", "---------", "-----",
     "----------", "-----"]
def show_summary_line_format(values: List[str]) -> str:
    return f"{values[0]:<18s}{values[1]:<7s}{values[2]:<8s}{values[3]:<11s}{values[4]:<7s}{values[5]:<12s}{values[6]}\n"

""" Show vrrp detail helpers """
SHOW_DETAIL_DIVIDER: str = \
    "--------------------------------------------------\n"
SHOW_DETAIL_INTF_DIVIDER: str=  "--------------\n"
def show_detail_intf_name(intf: str) -> str:
    return f"Interface: {intf}\n"
SHOW_DETAIL_GROUP_DIVIDER: str = "  ----------\n"
def show_detail_group_name(group: str) -> str:
    return f"  Group: {group}\n"
def show_detail_line_format(line: List[str]) -> str:
    return f"  {line[0]:<30s}{line[1]:<s}\n"
def show_detail_tracked_format(line: List[str]) -> str:
    return f"    {line[0]}   state {line[1]}      {line[2]}\n"
def show_detail_tracked_pmon_format(line: List[str]) -> str:
    return f"      {line[0]}  {line[1]}  {line[2]}\n"

""" Show vrrp statistics helpers """
def show_stats_header_format(line: List[str]) -> str:
    return f"  {line[0]}\n"
def show_stats_header_and_value_format(line: List[str]) -> str:
    return f"  {line[0]:<30s}{line[1]:<s}\n"
def show_stats_line_format(line: List[str]) -> str:
    return f"    {line[0]:<28s}{line[1]:<s}\n"

""" Show vrrp sync helpers """
def show_sync_group_name(group: str) -> str:
    return f"Group: {group}\n"
SHOW_SYNC_GROUP_DIVIDER: str = SHOW_DETAIL_GROUP_DIVIDER[3:]
def show_sync_group_state_format(state: str) -> str:
    return f"  State: {state}\n  Monitoring:\n"
def show_sync_group_members_format(line: List[str]) -> str:
    return f"    Interface: {line[0]}, Group: {line[1]}\n"

""" Functions to convert JSON/yang into show output"""

def show_vrrp_summary(state_dict: Dict) -> str:
    output: str = "\n"
    output += show_summary_line_format(SHOW_SUMMARY_HEADER_LINE_1)
    output += show_summary_line_format(SHOW_SUMMARY_HEADER_LINE_2)
    output += show_summary_line_format(SHOW_SUMMARY_HEADER_LINE_3)
    intf_type: str
    for intf_type in state_dict[util.INTERFACE_YANG_NAME]:
        intf_list: List = \
            state_dict[util.INTERFACE_YANG_NAME][intf_type]
        intf: Dict
        for intf in intf_list:
            intf_name: str = intf[util.TAGNODE_YANG]
            vrrp_instances: List = intf[util.VRRP_YANG_NAME][util.VRRP_GROUP_YANG]
            vrrp_instance: Dict
            for vrrp_instance in vrrp_instances:
                if util.INSTANCE_STATE_YANG not in vrrp_instance:
                    continue
                group: str  = vrrp_instance[util.TAGNODE_YANG]
                state: Dict  = vrrp_instance[util.INSTANCE_STATE_YANG]
                state_name: str  = state["state"]
                ipao: str 
                if state['address-owner']:
                    ipao = "yes"
                else:
                    ipao = "no"
                if state["rfc-interface"] == "":
                    rfc = "no"
                else:
                    rfc = state["rfc-interface"]
                sync: str 
                if state["sync-group"] == "":
                    sync = "<none>"
                else:
                    sync = state["sync-group"]
                now: int = calendar.timegm(time.localtime())
                last: int  = state["last-transition"]
                diff: int = now - last
                output += \
                    show_summary_line_format(
                        [intf_name, group, state_name, rfc, ipao,
                        util.elapsed_time(diff), sync]
                    )
    return output + "\n"


def show_vrrp_detail(
        state_dict: Dict,
        filter_intf: str = "",
        filter_grp: str = "") -> str:
    output: str = "\n"
    output += SHOW_DETAIL_DIVIDER
    intf_type: str
    for intf_type in state_dict[util.INTERFACE_YANG_NAME]:
        intf_list: List = \
            state_dict[util.INTERFACE_YANG_NAME][intf_type]
        intf: Dict
        for intf in intf_list:
            intf_name: str = intf[util.TAGNODE_YANG]
            if filter_intf != "" and intf_name != filter_intf:
                continue
            output += show_detail_intf_name(intf_name)
            output += SHOW_DETAIL_INTF_DIVIDER
            vrrp_instances: List = intf[util.VRRP_YANG_NAME][util.VRRP_GROUP_YANG]
            vrrp_instance: Dict
            for vrrp_instance in vrrp_instances:
                if util.INSTANCE_STATE_YANG not in vrrp_instance:
                    continue
                group: str = vrrp_instance[util.TAGNODE_YANG]
                if filter_grp != "" and group != filter_grp:
                    continue
                output += show_detail_group_name(group)
                output += SHOW_DETAIL_GROUP_DIVIDER
                state: Dict = vrrp_instance[util.INSTANCE_STATE_YANG]
                state_name: str = state["state"]
                output += show_detail_line_format(["State:", state_name])
                now: int = calendar.timegm(time.localtime())
                last: int = state["last-transition"]
                diff: int = now - last
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
                version: int = state["version"]
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
                    auth_value: Optional[str] = state["auth-type"]
                    if auth_value is None:
                        auth_value = "none"
                    output += show_detail_line_format(
                        ["Authentication type:", auth_value]
                    )

                preempt: str = "disabled"
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
                    accept: str = "disabled"
                    if state["accept"]:
                        accept = "enabled"
                    output += show_detail_line_format(
                        ["Accept:", accept]
                    )

                if state["sync-group"] != "":
                    output += "\n"
                    output += show_detail_line_format(
                        ["Sync-group:", state["sync-group"]]
                    )

                output += "\n"
                if "track" in state:
                    track: Dict = state["track"]
                    if "interface" in track:
                        output += show_detail_line_format(
                            ["Tracked Interfaces count:",
                            str(len(track["interface"]))]
                        )
                        track_intf: Dict
                        for track_intf in track["interface"]:
                            intf_weight: str = ""
                            if "weight" in track_intf:
                                intf_weight = f"weight {track_intf['weight']}"
                            output += show_detail_tracked_format(
                                [track_intf["name"], track_intf["state"],
                                intf_weight]
                            )
                    if "monitor" in track:
                        output += show_detail_line_format(
                            ["Tracked Path Monitor count:",
                            str(len(track["monitor"]))]
                        )
                        mont: Dict
                        for mont in track["monitor"]:
                            output += f"    {mont['name']}\n"
                            pol: Dict
                            for pol in mont["policies"]:
                                policy_weight: str = ""
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
                        route: Dict
                        for route in track["route"]:
                            route_weight: str = ""
                            if "weight" in route:
                                route_weight = f"weight {route['weight']}"
                            output += show_detail_tracked_format(
                                [route["name"], route["state"],
                                route_weight]
                            )
                output += show_detail_line_format(
                    ["VIP count:", str(len(state["virtual-ips"]))]
                )
                vip: str
                for vip in state["virtual-ips"]:
                    output += f"    {vip}\n"
                output += "\n"
    return output


def show_vrrp_interface(
        state_dict: Dict,
        filter_intf: str = "",
        filter_grp: str = "") -> str:
    output = show_vrrp_detail(state_dict, filter_intf, filter_grp)
    if output == f"\n{SHOW_DETAIL_DIVIDER}":
        output = f"VRRP is not running on {filter_intf}"
    elif output == f"\n{SHOW_DETAIL_DIVIDER}" + \
                   f"{show_detail_intf_name(filter_intf)}" + \
                   f"{SHOW_DETAIL_INTF_DIVIDER}":
        output = f"No VRRP group {filter_grp} exists on {filter_intf}"
    return output


def show_vrrp_sync(state_dict: Dict, specific: str = "") -> str:
    output: str = "\n"+SHOW_DETAIL_DIVIDER
    if (util.VRRP_YANG_NAME in state_dict):
        sync_group: Dict
        for sync_group in state_dict[util.VRRP_YANG_NAME]["sync-groups"]:
            if specific != "" and sync_group["name"] != specific:
                continue
            output += show_sync_group_name(
                sync_group["name"]
            )
            output += SHOW_SYNC_GROUP_DIVIDER
            output += show_sync_group_state_format(
                sync_group["state"]
            )
            group: str
            for group in sorted(sync_group["members"]):
                tokens: List[str] = group.split("-")
                output += show_sync_group_members_format(
                    tokens[1:]
                )
            output += "\n"
    if specific != "" and output == "\n"+SHOW_DETAIL_DIVIDER:
        output = f"\nSync-group: {specific} does not exist\n"
    return output

def show_vrrp_statistics(
        stats_dict: Dict,
        filter_intf: str = "",
        filter_grp: str = "") -> str:
    output: str = "\n"
    output += SHOW_DETAIL_DIVIDER
    intf_type: str
    for intf_type in stats_dict[util.INTERFACE_YANG_NAME]:
        intf_list: List = \
            stats_dict[util.INTERFACE_YANG_NAME][intf_type]
        intf: Dict
        for intf in intf_list:
            intf_name: str = intf[util.TAGNODE_YANG]
            if filter_intf != "" and intf_name != filter_intf:
                continue
            output += show_detail_intf_name(intf_name)
            output += SHOW_DETAIL_INTF_DIVIDER
            vrrp_instances: List = intf[util.VRRP_YANG_NAME][util.VRRP_GROUP_YANG]
            vrrp_instance: Dict
            for vrrp_instance in vrrp_instances:
                if util.INSTANCE_STATS_YANG not in vrrp_instance:
                    continue
                group: str = vrrp_instance[util.TAGNODE_YANG]
                if filter_grp != "" and group != filter_grp:
                    continue
                output += show_detail_group_name(group)
                output += SHOW_DETAIL_GROUP_DIVIDER
                stats: Dict = vrrp_instance[util.INSTANCE_STATS_YANG]
                key: str
                for key in stats:
                    if type(stats[key]) is dict:
                        subkey: str
                        key_name = f"{key}:"
                        output += show_stats_header_format([key_name, ""])
                        for subkey in stats[key]:
                            key_name = f"{subkey}:"
                            output += show_stats_line_format([key_name, stats[key][subkey]])
                        output += "\n"
                    else:
                        key_name = f"{key}:"
                        output += show_stats_header_and_value_format([key_name, stats[key]])
                        if key == "Released master":
                            output += "\n"
    return output

def show_vrrp_statistics_filters(
        stats_dict: Dict,
        filter_intf: str = "",
        filter_grp: str = "") -> str:
    output = show_vrrp_statistics(stats_dict, filter_intf, filter_grp)
    if output == f"\n{SHOW_DETAIL_DIVIDER}":
        output = f"VRRP is not running on {filter_intf}"
    elif output == f"\n{SHOW_DETAIL_DIVIDER}" + \
                   f"{show_detail_intf_name(filter_intf)}" + \
                   f"{SHOW_DETAIL_INTF_DIVIDER}":
        output = f"No VRRP group {filter_grp} exists on {filter_intf}"
    return output

""" Functions to convert files to JSON"""

def _get_end_of_tracking_config(
        config_block: List[str],
        last_config_index: int,
        interface_block: bool) -> int:
    while True:
        last_config_index += 1
        line = config_block[last_config_index]
        if not interface_block:
            if "Status" in line:
                last_config_index += 1
                line = config_block[last_config_index]
                if "Weight"  in line:
                    last_config_index += 1
                break
        else:
            if "Enabling" in line:
                last_config_index += 1
                break
    return last_config_index

def _convert_track_block_to_yang(config_block: List[str]) -> Dict[str, str]:
    tracked_obj: Dict[str, str] = {}
    for line in config_block:
        config_value = line.split()[-1]
        if "Name" in line or "Policy" in line or "Network" in line:
            tracked_obj["name"] = config_value
        elif "is UP" in line or "is Down" in line or "Status" in line:
            tracked_obj["state"] = config_value
        elif "weight" in line or "Weight" in line:
            tracked_obj["weight"] = config_value
        elif "Prefix" in line and "name" in tracked_obj:
            tracked_obj["name"] = tracked_obj["name"] + f"/{config_value}"
    return tracked_obj

def _convert_tracked_type_to_yang(
        config_block: List[str],
        block_indexes: List[int],
        end_of_config: int,
        offset: int,
        tracked_monitor_list: List[Any] = []) -> List[Any]:
    tracked_object_list: List[Any] = []
    for tracked_index in block_indexes:
        if tracked_monitor_list != []:
            monitor_name = config_block[tracked_index].split()[-1]
            for monitor in tracked_monitor_list:
                if monitor["name"] == monitor_name:
                    tracked_object_list = monitor["policies"]
        if tracked_index == block_indexes[-1]:
            track_block_end = end_of_config
        else:
            current_index = block_indexes.index(tracked_index)
            track_block_end = block_indexes[current_index + 1]
        tracked_object_list.append(_convert_track_block_to_yang(
            config_block[tracked_index+offset:track_block_end]
        ))
    if tracked_monitor_list != []:
        return tracked_monitor_list
    else:
        return tracked_object_list

def _prepopulate_pmon_tracking_list(config_block: List[str],
        block_indexes: List[int]) -> List[Dict[Any, Any]]:
    monitor_names: List[str] = []
    monitor_list: List[Dict[Any, Any]] = []
    for tracked_index in block_indexes:
        monitor_name: str = config_block[tracked_index].split()[-1]
        if monitor_name not in monitor_names:
            monitor_obj = {"name": monitor_name, "policies": []}
            monitor_names.append(monitor_name)
            monitor_list.append(monitor_obj)
    return monitor_list

def _convert_keepalived_data_to_yang(
        config_block: List[str], sync: str) -> Dict:
    """
    """

    instance_dict: Dict = {}
    key: str
    intf: str
    vrid: str
    instance_name: List[str]

    if config_block == []:
            return instance_dict

    instance_name = config_block[0].split("-")
    intf = instance_name[1]
    vrid = instance_name[2]
    instance_dict = \
        {
            "address-owner": "Address owner",
            "last-transition": "Last transition",
            "rfc-interface": "Transmitting device",
            "state": "State",
            "sync-group": sync,
            "version": "VRRP Version",
            "src-ip": "Using src_ip",
            "base-priority": "Base priority",
            "effective-priority": "Effective priority",
            "advert-interval": "Advert interval",
            "accept": "Accept",
            "preempt": "Preempt",
            "preempt-delay": "Preempt delay",
            "start-delay": "Start delay",
            "auth-type": "Authentication Type",
            "master-priority": "Master priority",
            "master-router": "Master router"
        }

    # Single line config code
    for key in instance_dict:
        if key == "sync-group":
            continue
        # Search for each term in the config
        config_exists: Tuple[bool, Union[List[None], str]] = \
            util.find_config_value(config_block, instance_dict[key])
        if not config_exists[0]:
            instance_dict[key] = config_exists[1]  # NOTFOUND

        if config_exists[1] != "NOTFOUND":
            split_line: List[str]
            if not isinstance(config_exists[1], list):
                split_line = config_exists[1].split()
                value = split_line[1]
                if key == "advert-interval":
                    if instance_dict["version"] == 2:
                        value = f"{value} sec"
                    else:
                        value = f"{value} milli-sec"
                elif key == "start-delay" or key == "preempt-delay":
                    value = f"{value} secs"
                elif key == "rfc-interface" and value == intf:
                    value = ""
                if value.isdigit():
                    # Term exists in config and has a numerical value
                    instance_dict[key] = int(value)
                elif value == "no" or value == "disabled":
                    instance_dict[key] = False
                elif value == "yes" or value == "enabled":
                    instance_dict[key] = True
                else:
                    instance_dict[key] = value
        else:
            if key == "auth-type":
                instance_dict[key] = None
            else:
                instance_dict[key] = "NOTFOUND"

    tracked_dict: Any
    tracked_dict = {}

    # Multi line config code
    track_intf_tuple: Tuple[bool, Union[List[None], str]] = \
            util.find_config_value(config_block, "Tracked interfaces =")
    tracked_pmon_tuple: Tuple[bool, Union[List[None], str]] = \
            util.find_config_value(config_block, "Tracked path-monitors =")
    track_route_tuple: Tuple[bool, Union[List[None], str]] = \
            util.find_config_value(config_block, "Tracked routes =")

    tracked_indexes: List[int]
    tracked_config_end: int
    config_start_offset: int =1

    if not isinstance(track_intf_tuple[1], list) and \
            track_intf_tuple[1] != "NOTFOUND":
        tracked_indexes = util.get_config_indexes(config_block, "------< NIC >------")
        tracked_config_end = _get_end_of_tracking_config(
            config_block, tracked_indexes[-1], True)
        tracked_dict["interface"] = _convert_tracked_type_to_yang(config_block,
            tracked_indexes, tracked_config_end, config_start_offset)

    if not isinstance(tracked_pmon_tuple[1], list) and \
            tracked_pmon_tuple[1] != "NOTFOUND":
        tracked_indexes = util.get_config_indexes(
            config_block, "Monitor"
        )
        tracked_config_end = _get_end_of_tracking_config(
            config_block, tracked_indexes[-1], False)
        tracked_monitor_list = _prepopulate_pmon_tracking_list(config_block,
            tracked_indexes)
        tracked_dict["monitor"] = _convert_tracked_type_to_yang(config_block,
            tracked_indexes, tracked_config_end, config_start_offset,
            tracked_monitor_list)

    if not isinstance(track_route_tuple[1], list) and \
            track_route_tuple[1] != "NOTFOUND":
        tracked_indexes = util.get_config_indexes(config_block, "Network")
        tracked_config_end = _get_end_of_tracking_config(
            config_block, tracked_indexes[-1], False)
        config_start_offset = 0
        tracked_dict["route"] = _convert_tracked_type_to_yang(config_block,
            tracked_indexes, tracked_config_end, config_start_offset)


    if tracked_dict != {}:
        instance_dict["track"] = tracked_dict

    vip_tuple: Tuple[bool, Union[List[None], str]] = \
            util.find_config_value(config_block, "Virtual IP =")
    num_vips: int 
    if not isinstance(vip_tuple[1], list):
        num_vips = int(vip_tuple[1])
        vips_start = util.get_config_indexes(config_block, "Virtual IP")[0]
        vips_end = vips_start + num_vips + 1
        virtual_addresses = []
        for address in config_block[vips_start+1:vips_end]:
            virtual_addresses.append(address.split()[0])
        instance_dict["virtual-ips"] = virtual_addresses

    instance_dict = \
            {key: val for key, val in instance_dict.items() if val != "NOTFOUND"}

    #instance_dict = \
    #    {key: instance_dict[key] for key in sorted(instance_dict.keys())}
    return {"instance-state": instance_dict, "tagnode": vrid}

def convert_data_file_to_dict(data_string: str):
    data_dict: dict
    config_indexes: List[int]
    config_blocks: List[List[str]]
    data_list: List[str]

    yang_representation: Dict[str, Dict] = {
        util.INTERFACE_YANG_NAME: {}
    }
    data_list = data_string.split("\n")
    config_indexes = util.get_config_indexes(data_list, "VRRP Instance")
    config_blocks = util.get_config_blocks(data_list, config_indexes)

    sync_group_start_indexes: List[int] = util.get_config_indexes(
        data_list, "VRRP Sync Group")
    sync_group_instances: Dict = {}
    if sync_group_start_indexes != []:
        yang_representation[util.VRRP_YANG_NAME] = {"sync-groups": []}
        sync_group_data_list = data_list[sync_group_start_indexes[0]:]
        sync_group_start_indexes = util.get_config_indexes(
            sync_group_data_list, "VRRP Sync Group")
        sync_group_config: List[str] = util.get_config_blocks(
            sync_group_data_list,
            sync_group_start_indexes
        )

        sync_group: str
        for sync_group in sync_group_config:
            sync_group_show_dict: Dict[str, Union[str, List[str]]] = {}
            group_name_exists: Tuple[bool, str] = \
                util.find_config_value(sync_group, "VRRP Sync Group")
            if not group_name_exists[0]:
                continue
            group_tokens: List[str] = group_name_exists[1].split()
            group_name: str = group_tokens[1][:-1]
            sync_group_show_dict["name"] = group_name
            sync_group_show_dict["state"] = group_tokens[-1]
            sync_group_show_dict["members"] = []
            for instance in sync_group[1:]:
                if instance == "":
                    continue
                tokens = instance.split()
                sync_group_instances[tokens[-1]] = group_name
                if isinstance(sync_group_show_dict["members"], list):
                    sync_group_show_dict["members"].append(tokens[-1])
            yang_representation[util.VRRP_YANG_NAME]["sync-groups"].append(
                sync_group_show_dict
            )

    for block in config_blocks:
        instance_tokens: List[str] = block[0].split()
        instance_name: str = instance_tokens[-1]
        sync: str = ""
        if instance_name in sync_group_instances:
            sync = sync_group_instances[instance_name]
        else:
            sync = ""
        instance_dict = _convert_keepalived_data_to_yang(block, sync)

        intf_name: str = instance_name.split("-")[1]
        vif_number: str = ""
        if "." in intf_name:
            vif_sep: List[str] = intf_name.split(".")
            intf_name = vif_sep[0]
            vif_number = vif_sep[1]
        interface_list: Dict[Any, Any] = yang_representation[util.INTERFACE_YANG_NAME]
        # Find the interface type for the interface name, right now this
        # is just a guess, there might be a better method of doing this
        # than regexes
        intf_type: str = util.intf_name_to_type(intf_name)[0]
        if intf_type not in interface_list:
            interface_list[intf_type] = []
        interface_list = interface_list[intf_type]

        # Hackery to find the reference to the interface this vrrp
        # group should be added to.
        insertion_reference: List[Dict] = util.find_interface_in_yang_repr(
            intf_name, vif_number, interface_list)

        insertion_reference[util.VRRP_YANG_NAME]["vrrp-group"].append(instance_dict)
        del(insertion_reference[util.VRRP_YANG_NAME]["start-delay"])

    return yang_representation

def _convert_keepalived_stats_to_yang(
        config_block: List[str]) -> Dict:
    """
    """

    instance_dict: Dict = {}
    key: str
    intf: str
    vrid: str

    if config_block == []:
        return instance_dict

    instance_name = config_block[0].split("-")
    intf = instance_name[1]
    vrid = instance_name[2]
    ADVERT_KEY: str = "Advertisements"
    RECV_KEY: str = "Received"
    SENT_KEY: str = "Sent"
    BECOME_KEY: str = "Became master"
    RELEASE_KEY: str = "Released master"
    PACKET_KEY: str = "Packet errors"
    LENGTH_KEY: str = "Length"
    TTL_KEY: str = "TTL"
    INVALID_TYPE_KEY: str = "Invalid type"
    ADVERT_INTERVAL_KEY: str = "Advertisement interval"
    ADDRESS_LIST_KEY: str = "Address list"
    AUTH_ERROR_KEY: str = "Authentication errors"
    TYPE_MISMATCH_KEY: str = "Type mismatch"
    FAILURE_KEY: str = "Failure"
    PZERO_SEARCH_STR: str = "Priority zero"
    PZERO_KEY: str = f"{PZERO_SEARCH_STR} {ADVERT_KEY.casefold()}"

    instance_dict = \
        {
            ADVERT_KEY: {
                RECV_KEY: "",
                SENT_KEY: ""
            },
            BECOME_KEY: "",
            RELEASE_KEY: "",
            PACKET_KEY: {
                LENGTH_KEY: "",
                TTL_KEY: "",
                INVALID_TYPE_KEY: "",
                ADVERT_INTERVAL_KEY: "",
                ADDRESS_LIST_KEY: ""
            },
            AUTH_ERROR_KEY: {
                INVALID_TYPE_KEY: "",
                TYPE_MISMATCH_KEY: "",
                FAILURE_KEY: 0
            },
            PZERO_KEY: {
                RECV_KEY: "",
                SENT_KEY: ""
            }
        }

    # Single line config code
    config_index: int = 0
    value: List[str]
    while config_index < len(config_block):
        line: str = config_block[config_index].casefold()
        if ADVERT_KEY.casefold() in line:
            for key in instance_dict[ADVERT_KEY]:
                config_index += 1
                value = config_block[config_index].split()
                instance_dict[ADVERT_KEY][key] = value[-1]
        elif BECOME_KEY.casefold() in line:
            value = config_block[config_index].split()
            instance_dict[BECOME_KEY] = value[-1]
        elif RELEASE_KEY.casefold() in line:
            value = config_block[config_index].split()
            instance_dict[RELEASE_KEY] = value[-1]
        elif PACKET_KEY.casefold() in line:
            for key in instance_dict[PACKET_KEY]:
                config_index += 1
                value = config_block[config_index].split()
                instance_dict[PACKET_KEY][key] = value[-1]
        elif AUTH_ERROR_KEY.casefold() in line:
            for key in instance_dict[AUTH_ERROR_KEY]:
                config_index += 1
                value = config_block[config_index].split()
                instance_dict[AUTH_ERROR_KEY][key] = value[-1]
        elif PZERO_SEARCH_STR.casefold() in line:
            for key in instance_dict[PZERO_KEY]:
                config_index += 1
                value = config_block[config_index].split()
                instance_dict[PZERO_KEY][key] = value[-1]
        config_index += 1

    return {"stats": instance_dict, "tagnode": int(vrid)}

def convert_stats_file_to_dict(data_string: str):
    data_dict: dict
    config_indexes: List[int]
    config_blocks: List[List[str]]
    data_list: List[str]

    yang_representation: Dict[str, Dict] = {
        util.INTERFACE_YANG_NAME: {}
    }
    data_list = data_string.split("\n")
    config_indexes = util.get_config_indexes(data_list, "VRRP Instance")
    config_blocks = util.get_config_blocks(data_list, config_indexes)

    for block in config_blocks:
        instance_tokens: List[str] = block[0].split()
        instance_name: str = instance_tokens[-1]

        instance_dict = _convert_keepalived_stats_to_yang(block)

        intf_name: str = instance_name.split("-")[1]
        vif_number: str = ""
        if "." in intf_name:
            vif_sep: List[str] = intf_name.split(".")
            intf_name = vif_sep[0]
            vif_number = vif_sep[1]
        interface_list: Dict[Any, Any] = yang_representation[util.INTERFACE_YANG_NAME]
        # Find the interface type for the interface name, right now this
        # is just a guess, there might be a better method of doing this
        # than regexes
        intf_type: str = util.intf_name_to_type(intf_name)[0]
        if intf_type not in interface_list:
            interface_list[intf_type] = []
        interface_list = interface_list[intf_type]

        # Hackery to find the reference to the interface this vrrp
        # group should be added to.
        insertion_reference: List[Dict] = util.find_interface_in_yang_repr(
            intf_name, vif_number, interface_list)

        insertion_reference[util.VRRP_YANG_NAME]["vrrp-group"].append(instance_dict)
        del(insertion_reference[util.VRRP_YANG_NAME]["start-delay"])

    return yang_representation