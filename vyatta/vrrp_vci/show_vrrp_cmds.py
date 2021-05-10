# Copyright (c) 2020,2021 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import time
from typing import Any, Dict, List, Optional, Union

import vyatta.vrrp_vci.keepalived.util as util

""" Show VRRP summary helpers. """
SHOW_SUMMARY_HEADER_LINE_1: List[str] = (
    ["", "", "", "RFC", "Addr", "Last", "Sync"])
SHOW_SUMMARY_HEADER_LINE_2: List[str] = (
    ["Interface", "Group", "State", "Compliant", "Owner",
     "Transition", "Group"])
SHOW_SUMMARY_HEADER_LINE_3: List[str] = (
    ["---------", "-----", "-----", "---------", "-----",
     "----------", "-----"]
)


def show_summary_line_format(values: List[str]) -> str:
    return (f"{values[0]:<18s}{values[1]:<7s}{values[2]:<8s}"
            f"{values[3]:<11s}{values[4]:<7s}{values[5]:<12s}"
            f"{values[6]}\n")


""" Show VRRP detail helpers. """


SHOW_DETAIL_DIVIDER: str = (
    "--------------------------------------------------\n")
SHOW_DETAIL_INTF_DIVIDER: str = "--------------\n"


def show_detail_intf_name(intf: str) -> str:
    return f"{util.YANG_INTERFACE_CONST.capitalize()}: {intf}\n"


SHOW_DETAIL_GROUP_DIVIDER: str = "  ----------\n"


def show_detail_group_name(group: str) -> str:
    return f"  Group: {group}\n"


def show_detail_line_format(line: List[str]) -> str:
    return f"  {line[0]:<30s}{line[1]:<s}\n"


def show_detail_tracked_format(line: List[str]) -> str:
    return f"    {line[0]}   {util.YANG_STATE} {line[1]}      {line[2]}\n"


def show_detail_tracked_format_without_weight(line: List[str]) -> str:
    return f"    {line[0]}   {util.YANG_STATE} {line[1]}\n"


def show_detail_tracked_pmon_format(line: List[str]) -> str:
    return f"      {line[0]}  {line[1]}  {line[2]}\n"


def show_detail_tracked_pmon_format_without_weight(line: List[str]) -> str:
    return f"      {line[0]}  {line[1]}\n"


""" Show VRRP statistics helpers. """


def show_stats_header_format(line: List[str]) -> str:
    return f"  {line[0]}\n"


def show_stats_header_and_value_format(line: List[str]) -> str:
    return f"  {line[0]:<30s}{line[1]:<s}\n"


def show_stats_line_format(line: List[str]) -> str:
    return f"    {line[0]:<28s}{line[1]:<s}\n"


""" Show VRRP sync helpers """


def show_sync_group_name(group: str) -> str:
    return f"Group: {group}\n"


SHOW_SYNC_GROUP_DIVIDER: str = SHOW_DETAIL_GROUP_DIVIDER[3:]


def show_sync_group_state_format(state: str) -> str:
    return f"  State: {state}\n  Monitoring:\n"


def show_sync_group_members_format(line: List[str]) -> str:
    return f"    Interface: {line[0]}, Group: {line[1]}\n"


""" Functions to convert JSON/yang into show output. """


def show_vrrp_summary(state_dict: Dict) -> str:
    """
    Convert a YANG like python dictionary into the "show vrrp" string
    representation. This is done by running over the state_dict and for
    every VRRP group calling show_summary_line_format() with a list of
    the values in the group's instance-state dictionary.

    Arguments:
        state_dict a python dictionary of the following format:
        {
            "vyatta-interfaces-v1:interfaces":{
                "vyatta-interfaces-dataplane-v1:dataplane":
                    [
                        {
                            "tagnode":"dp0p1s1",
                            "vyatta-vrrp-v1:vrrp": {
                                "start-delay": 0,
                                "vrrp-group":[
                                    {
                                        "tagnode":1,
                                        "instance-state":
                                            {
                                                "address-owner": False,
                                                "last-transition": 0,
                                                "rfc-interface": "",
                                                "state": "MASTER",
                                                "sync-group": "",
                                            },
                                        "accept":false,
                                        "preempt":true,
                                        "version":2,
                                        "virtual-address":["10.10.1.100/25"]
                                    }
                                ]
                            }
                        }
                    ]
                }
        }
    Returns:
        A string representing the show output:
                                         RFC        Addr   Last        Sync
        Interface         Group  State   Compliant  Owner  Transition  Group
        ---------         -----  -----   ---------  -----  ----------  -----
        dp0p1s1           1      MASTER  no         no     3s          <none>

    N.B.
    The yang format passed to this function is taken directly from the state
    calls from the VCI component, not from the keepalived.data file conversion
    (both should hold the same data).
    """

    state_dict = util.sanitize_vrrp_config(state_dict)

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
            intf_name_key: str = util.get_namespace(
                intf, util.YANG_INTERFACE_NAMESPACE
            )
            if intf_name_key == "":
                continue
            intf_name: str = intf[intf_name_key]
            current_vrrp_namespace: str = util.get_namespace(
                intf, util.VRRP_YANG_NAMESPACES
            )
            if current_vrrp_namespace == "":
                continue
            vrrp_instances: List = \
                intf[current_vrrp_namespace][util.YANG_VRRP_GROUP]
            vrrp_instance: Dict
            for vrrp_instance in vrrp_instances:
                if util.YANG_INSTANCE_STATE not in vrrp_instance:
                    continue
                group: str = vrrp_instance[util.YANG_TAGNODE]
                state: Dict = vrrp_instance[util.YANG_INSTANCE_STATE]
                state_name: str = state[util.YANG_STATE]
                ipao: str
                if util.YANG_IPAO not in state:
                    state[util.YANG_IPAO] = False
                if state[util.YANG_IPAO]:
                    ipao = util.SHOW_IPAO_YES
                else:
                    ipao = util.SHOW_IPAO_NO
                if state[util.YANG_RFC_INTF] == "":
                    rfc = util.SHOW_IPAO_NO
                else:
                    rfc = state[util.YANG_RFC_INTF]
                sync: str
                if state[util.YANG_SYNC_GROUP] == "":
                    sync = f"<{util.SHOW_SG_VALUE}>"
                else:
                    sync = state[util.YANG_SYNC_GROUP]
                now: int = int(time.time())
                last: int = int(float(state[util.YANG_LAST_TRANSITION]))
                diff: int = now - last
                output += \
                    show_summary_line_format(
                        [intf_name, group, state_name, rfc, ipao,
                         util.elapsed_time(diff), sync])
    return output + "\n"


def show_vrrp_detail(
    state_dict: Dict,
    filter_intf: str = "",
    filter_grp: str = ""
) -> str:
    """
    Convert a YANG like python dictionary into the "show vrrp detail" string
    representation.
    This is done by running over the state_dict, and for every VRRP group
    calling the show_detail_*() functions on the relevant value in the
    group's instance-state dictionary.

    Arguments:
        state_dict: a python dictionary containing full state information.
        {
            "vyatta-interfaces-v1:interfaces":{
                "vyatta-interfaces-dataplane-v1:dataplane":
                    [
                        {
                            "tagnode":"dp0p1s1",
                            "vyatta-vrrp-v1:vrrp": {
                                "vrrp-group":[
                                    {
                                        "tagnode":1,
                                        "instance-state":
                                            {
                                                "address-owner": False,
                                                "last-transition": 0,
                                                "rfc-interface": "",
                                                "state": "MASTER",
                                                "sync-group": "",
                                                "version": 2,
                                                "src-ip": "10.10.1.1",
                                                "base-priority": 100,
                                                "effective-priority": 100,
                                                "advert-interval": "2 sec",
                                                "accept": True,
                                                "preempt": True,
                                                "auth-type": None,
                                                "virtual-ips": [
                                                    "10.10.1.100/32"
                                                ]
                                            }
                                    }
                                ]
                            }
                        }
                    ]
                }
        }
        filter_intf: A string to filter the output down to.
        filter_grp:
            A string to filter the output down to
            (must also be called with a filter_intf).
    Returns:
        A string for the "show vrrp detail" call of similar format to:
        --------------------------------------------------
        Interface: dp0p1s1
        --------------
          Group: 1
          ----------
          State:                        MASTER
          Last transition:              3s

          Version:                      2
          Configured Priority:          100
          Effective Priority:           100
          Advertisement interval:       2 sec
          Authentication type:          none
          Preempt:                      enabled

          VIP count:                    1
            10.10.1.100/32

    N.B.
    The yang format passed to this function is converted from the
    keepalived.data file by other functions and passed here to generate
    the show output. If an interface or an interface and a group are
    passed to this function then the output is filtered to just the
    requested information.
    """

    state_dict = util.sanitize_vrrp_config(state_dict)

    output: str = "\n"
    output += SHOW_DETAIL_DIVIDER
    intf_type: str
    for intf_type in state_dict[util.INTERFACE_YANG_NAME]:
        intf_list: List = \
            state_dict[util.INTERFACE_YANG_NAME][intf_type]
        intf: Dict
        for intf in intf_list:
            intf_name: str = intf[util.YANG_TAGNODE]
            if filter_intf != "" and intf_name != filter_intf:
                continue
            output += show_detail_intf_name(intf_name)
            output += SHOW_DETAIL_INTF_DIVIDER
            current_vrrp_namespace: str = util.get_namespace(
                intf, util.VRRP_YANG_NAMESPACES
            )
            if current_vrrp_namespace == "":
                continue
            vrrp_instances: List = \
                intf[current_vrrp_namespace][util.YANG_VRRP_GROUP]
            vrrp_instance: Dict
            for vrrp_instance in vrrp_instances:
                if util.YANG_INSTANCE_STATE not in vrrp_instance:
                    continue
                group: str = vrrp_instance[util.YANG_TAGNODE]
                if filter_grp != "" and int(group) != int(filter_grp):
                    continue
                output += show_detail_group_name(group)
                output += SHOW_DETAIL_GROUP_DIVIDER
                state: Dict = vrrp_instance[util.YANG_INSTANCE_STATE]
                state_name: str = state[util.YANG_STATE]
                if state_name == util.VrrpState.TRANSIENT.value:
                    state_name = util.VrrpState.INIT.name
                output += show_detail_line_format(
                    [f"{util.YANG_STATE.title()}:", state_name])
                now: int = int(time.time())
                last: int = int(float(state[util.YANG_LAST_TRANSITION]))
                diff: int = now - last
                output += show_detail_line_format(
                    [f"{util.SHOW_LAST_TRANSITION}:", util.elapsed_time(diff)]
                )

                if state_name == util.VrrpState.BACKUP.name:
                    output += "\n"
                    output += show_detail_line_format(
                        [f"{util.SHOW_MASTER_ROUTER}:",
                         state[util.YANG_MASTER_ROUTER_STATE]]
                    )
                    output += show_detail_line_format(
                        [f"{util.SHOW_MASTER_PRIORITY}:",
                         str(state[util.YANG_MASTER_PRIO_STATE])]
                    )

                output += "\n"
                version: int = state[util.YANG_VERSION]
                output += show_detail_line_format(
                    [f"{util.SHOW_VERSION}:", str(version)]
                )

                if state[util.YANG_RFC_INTF] != "":
                    output += show_detail_line_format(
                        [f"{util.SHOW_RFC_COMPAT}", ""]
                    )
                    output += show_detail_line_format(
                        [f"{util.SHOW_VMAC_INTF}:",
                         state[util.YANG_RFC_INTF].replace(",", "")]
                    )
                if util.YANG_IPAO not in state:
                    state[util.YANG_IPAO] = False
                if state[util.YANG_IPAO]:
                    output += show_detail_line_format(
                        [f"{util.SHOW_IPAO}:", util.SHOW_IPAO_YES]
                    )
                    output += "\n"
                elif state[util.YANG_RFC_INTF] != "":
                    output += show_detail_line_format(
                        [f"{util.SHOW_IPAO}:", util.SHOW_IPAO_NO]
                    )
                    output += "\n"
                    output += show_detail_line_format(
                        [f"{util.SHOW_SOURCE_ADDR}:",
                         state[util.YANG_SRC_IP_STATE]]
                    )

                output += show_detail_line_format(
                    [f"{util.SHOW_CONFIG_PRIORITY}:",
                     str(state[util.YANG_BASE_PRIO])]
                )
                output += show_detail_line_format(
                    [f"{util.SHOW_EFFECTIVE_PRIORITY}:",
                     str(state[util.YANG_EFFECTIVE_PRIO])]
                )
                output += show_detail_line_format(
                    [f"{util.SHOW_ADVERT_INT}:",
                     state[util.YANG_ADVERT_INT_STATE]]
                )
                if version == 2:
                    auth_value: Optional[str] = state[util.YANG_AUTH_TYPE]
                    if auth_value is None:
                        auth_value = util.SHOW_SG_VALUE
                    output += show_detail_line_format(
                        [f"{util.SHOW_AUTH_TYPE}:",
                         auth_value]
                    )

                preempt: str = util.SHOW_PREEMPT_DISABLED
                if state[util.YANG_PREEMPT]:
                    preempt = util.SHOW_PREEMPT_ENABLED
                output += show_detail_line_format(
                    [f"{util.SHOW_PREEMPT}:", preempt]
                )
                if util.YANG_PREEMPT_DELAY in state:
                    output += show_detail_line_format(
                        [f"{util.SHOW_PREEMPT_DELAY}:",
                         state[util.YANG_PREEMPT_DELAY]]
                    )

                if util.YANG_START_DELAY in state:
                    output += show_detail_line_format(
                        [f"{util.SHOW_START_DELAY}:",
                         state[util.YANG_START_DELAY]]
                    )

                if version == 3:
                    accept: str = util.SHOW_PREEMPT_DISABLED
                    if state[util.YANG_ACCEPT]:
                        accept = util.SHOW_PREEMPT_ENABLED
                    output += show_detail_line_format(
                        [f"{util.SHOW_ACCEPT}:", accept]
                    )

                if state[util.YANG_SYNC_GROUP] != "":
                    output += "\n"
                    output += show_detail_line_format(
                        [f"{util.SHOW_SYNC_GROUP}:",
                         state[util.YANG_SYNC_GROUP]]
                    )

                output += "\n"
                if util.YANG_TRACK in state:
                    track: Dict = state[util.YANG_TRACK]
                    if util.YANG_INTERFACE_CONST in track:
                        output += show_detail_line_format(
                            [f"{util.SHOW_TRACK_INTF_COUNT}:",
                             str(len(track[util.YANG_INTERFACE_CONST]))]
                        )
                        track_intf: Dict
                        for track_intf in \
                                sorted(track[util.YANG_INTERFACE_CONST],
                                       key=lambda k: k[util.YANG_NAME]):
                            intf_weight: str = ""
                            if util.YANG_TRACK_WEIGHT in track_intf:
                                intf_weight = (
                                    f"{util.YANG_TRACK_WEIGHT} "
                                    f"{track_intf[util.YANG_TRACK_WEIGHT]}"
                                )
                                output += show_detail_tracked_format(
                                    [track_intf[util.YANG_NAME],
                                     track_intf[util.YANG_STATE],
                                     intf_weight]
                                )
                            else:
                                output += \
                                    show_detail_tracked_format_without_weight(
                                        [track_intf[util.YANG_NAME],
                                         track_intf[util.YANG_STATE]]
                                    )
                    if util.YANG_TRACK_MONITOR in track:
                        track_output: str = ""
                        tracked_count: int = 0
                        mont: Dict
                        for mont in track[util.YANG_TRACK_MONITOR]:
                            track_output += f"    {mont[util.YANG_NAME]}\n"
                            pol: Dict
                            for pol in sorted(mont[util.SHOW_POLICIES],
                                              key=lambda k: k[util.YANG_NAME]):
                                tracked_count += 1
                                policy_weight: str = ""
                                if util.YANG_TRACK_WEIGHT in pol:
                                    policy_weight = (
                                        f"{util.YANG_TRACK_WEIGHT} "
                                        f"{pol[util.YANG_TRACK_WEIGHT]}"
                                    )
                                    track_output += \
                                        show_detail_tracked_pmon_format(
                                            [pol[util.YANG_NAME],
                                             pol[util.YANG_STATE],
                                             policy_weight]
                                        )
                                else:
                                    track_output += \
                                        show_detail_tracked_pmon_format_without_weight(  # noqa: E501
                                            [pol[util.YANG_NAME],
                                             pol[util.YANG_STATE],
                                             policy_weight]
                                        )
                        output += show_detail_line_format(
                            [f"{util.SHOW_TRACK_PMON_COUNT}:",
                             str(tracked_count)]
                        )
                        output += track_output
                    if util.YANG_TRACK_ROUTE in track:
                        output += show_detail_line_format(
                            [f"{util.SHOW_TRACK_ROUTES_COUNT}:",
                             str(len(track[util.YANG_TRACK_ROUTE]))]
                        )
                        route: Dict
                        for route in sorted(track[util.YANG_TRACK_ROUTE],
                                            key=lambda k: k[util.YANG_NAME]):
                            route_weight: str = ""
                            if util.YANG_TRACK_WEIGHT in route:
                                route_weight = (
                                    f"{util.YANG_TRACK_WEIGHT} "
                                    f"{route[util.YANG_TRACK_WEIGHT]}")
                                output += \
                                    show_detail_tracked_format(
                                        [route[util.YANG_NAME],
                                         route[util.YANG_STATE],
                                         route_weight]
                                    )
                            else:
                                output += \
                                    show_detail_tracked_format_without_weight(
                                        [route[util.YANG_NAME],
                                         route[util.YANG_STATE]]
                                    )
                output += show_detail_line_format(
                    [f"{util.SHOW_VIP_COUNT}:",
                     str(len(state[util.YANG_VIP_STATE]))]
                )
                vip: str
                for vip in state[util.YANG_VIP_STATE]:
                    if "/" not in vip:
                        if "." in vip:
                            vip = f"{vip}/32"
                        else:
                            vip = f"{vip}/128"
                    output += f"    {vip}\n"
                output += "\n"
    return output


def show_vrrp_interface(
    state_dict: Dict,
    filter_intf: str = "",
    filter_grp: str = ""
) -> str:
    """
    Function to be called from vyatta-show-vrrp.py to match the existing
    "show vrrp interface" output. The output of "show vrrp interface" is the
    same as "show vrrp detail" with filters applied.

    Arguments:
        state_dict: a python dictionary containing full state information.
        filter_intf: A string to filter the output down to.
        filter_grp:
            A string to filter the output down to
            (must also be called with a filter_intf).
    Returns:
        A string for the "show vrrp interface <intf> group <vrid>" call.
    """

    output = show_vrrp_detail(state_dict, filter_intf, filter_grp)
    if output == f"\n{SHOW_DETAIL_DIVIDER}":
        output = f"VRRP is not running on {filter_intf}"
    elif output == (f"\n{SHOW_DETAIL_DIVIDER}"
                    f"{show_detail_intf_name(filter_intf)}"
                    f"{SHOW_DETAIL_INTF_DIVIDER}"):
        output = f"No VRRP group {filter_grp} exists on {filter_intf}"
    return output


def show_vrrp_sync(state_dict: Dict, specific: str = "") -> str:
    """
    Convert a YANG like python dictionary into the "show vrrp sync-group"
    string representation.
    This is done by running over the vyatta-vrrp-v1:vrrp/sync-groups list
    in the state_dict and for every sync_group calling the show_sync_group_*()
    functions on the relevant value in the sync-group's dictionary.

    Arguments:
        state_dict: a python dictionary containing full state information
                    and sync group information.
        {
            "vyatta-interfaces-v1:interfaces":{
                "vyatta-interfaces-dataplane-v1:dataplane":
                    [
                        {
                            "tagnode":"dp0p1s1",
                            "vyatta-vrrp-v1:vrrp": {
                                "vrrp-group":[
                                    {
                                        "tagnode":1,
                                        "instance-state":
                                            {
                                                "address-owner": False,
                                                "last-transition": 0,
                                                "rfc-interface": "",
                                                "state": "MASTER",
                                                "sync-group": "",
                                            },
                                        "accept":false,
                                        "preempt":true,
                                        "version":2,
                                        "virtual-address":["10.10.1.100/25"]
                                    }
                                ]
                            }
                        }
                    ]
                },
            "vyatta-vrrp-v1:vrrp":
                {
                    "sync-groups":
                    [
                        {
                            "name": "TEST",
                            "state": "MASTER",
                            "members": [
                                "vyatta-dp0p1s2-1",
                                "vyatta-dp0p1s1-1"
                            ]
                        }
                    ]
                }
        }
        specific: The name of a specific sync-group, used to filter the output
                  to that group
    Returns:
        A string for the "show vrrp sync" call of similar format to:
        --------------------------------------------------
        Group: TEST
        ---------
          State: MASTER
          Monitoring:
            Interface: dp0p1s1, Group: 1
            Interface: dp0p1s2, Group: 1

    N.B.
    The yang format passed to this function is created from the same function
    that reads the keepalived.data file as that's where the syncgroup
    information is held.
    """

    output: str = f"\n{SHOW_DETAIL_DIVIDER}"
    if util.VRRP_YANG_NAME in state_dict:
        sync_group: Dict
        for sync_group in \
                state_dict[util.VRRP_YANG_NAME][f"{util.YANG_SYNC_GROUP}s"]:
            if specific != "" and sync_group[util.YANG_NAME] != specific:
                continue
            output += show_sync_group_name(
                sync_group[util.YANG_NAME]
            )
            output += SHOW_SYNC_GROUP_DIVIDER
            output += show_sync_group_state_format(
                sync_group[util.YANG_STATE]
            )
            group: str
            for group in sorted(sync_group[util.YANG_SG_MEMBER]):
                tokens: List[str] = group.split("-")
                output += show_sync_group_members_format(
                    tokens[1:]
                )
            output += "\n"
    if specific != "" and output == f"\n{SHOW_DETAIL_DIVIDER}":
        output = f"\nSync-group: {specific} does not exist\n"
    return output


def show_vrrp_statistics(
    stats_dict: Dict,
    filter_intf: str = "",
    filter_grp: str = ""
) -> str:
    """
    Convert a YANG like python dictionary into the "show vrrp statistics"
    string representation.
    This is done by running over the stats_dict, and for every VRRP group
    calling the show_stats_*() functions on the relevant value in the
    group's stats dictionary.

    Arguments:
        stats_dict: a python dictionary containing full statistics information.
        {
            "vyatta-interfaces-v1:interfaces":{
                "vyatta-interfaces-dataplane-v1:dataplane":
                    [
                        {
                            "tagnode":"dp0p1s1",
                            "vyatta-vrrp-v1:vrrp": {
                                "vrrp-group":[
                                    {
                                        "tagnode":1,
                                        "stats": {
                                            "Advertisements": {
                                                "Received": "0",
                                                "Sent": "615"
                                            },
                                            "Became master": "1",
                                            "Released master": "0",
                                            "Packet errors": {
                                                "Length": "0",
                                                "TTL": "0",
                                                "Invalid type": "0",
                                                "Advertisement interval": "0",
                                                "Address list": "0"
                                            },
                                            "Authentication errors": {
                                                "Invalid type": "0",
                                                "Type mismatch": "0",
                                                "Failure": "0"
                                            },
                                            "Priority zero advertisements": {
                                                "Received": "0",
                                                "Sent": "0"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
        }
        filter_intf: A string to filter the output down to.
        filter_grp:
            A string to filter the output down to
            (must also be called with a filter_intf).
    Returns:
        A string for the "show vrrp statistics" call of similar format to:
        --------------------------------------------------
        Interface: dp0p1s1
            --------------
              Group: 1
              ----------
              Advertisements:
                Received:                   0
                Sent:                       615

              Became master:                1
              Released master:              0

              Packet errors:
                Length:                     0
                TTL:                        0
                Invalid type:               0
                Advertisement interval:     0
                Address list:               0

              Authentication errors:
                Invalid type:               0
                Type mismatch:              0
                Failure:                    0

              Priority zero advertisements:
                Received:                   0
                Sent:                       0

    N.B.
    The yang format passed to this function is created from the
    keepalived.stats file. The show output has been tidied up to be more
    consistent, some entries from the legacy implementation would have
    all first letters capitalised some would have only the first.
    The stats can be filtered in a similar way to show vrrp detail, on
    interface or on interface and group.
    """

    stats_dict = util.sanitize_vrrp_config(stats_dict)

    output: str = "\n"
    output += SHOW_DETAIL_DIVIDER
    intf_type: str
    for intf_type in stats_dict[util.INTERFACE_YANG_NAME]:
        intf_list: List = \
            stats_dict[util.INTERFACE_YANG_NAME][intf_type]
        intf: Dict
        for intf in intf_list:
            intf_name: str = intf[util.YANG_TAGNODE]
            if filter_intf != "" and intf_name != filter_intf:
                continue
            output += show_detail_intf_name(intf_name)
            output += SHOW_DETAIL_INTF_DIVIDER
            current_vrrp_namespace: str = util.get_namespace(
                intf, util.VRRP_YANG_NAMESPACES
            )
            if current_vrrp_namespace == "":
                continue
            vrrp_instances: List = \
                intf[current_vrrp_namespace][util.YANG_VRRP_GROUP]
            vrrp_instance: Dict
            for vrrp_instance in vrrp_instances:
                if util.YANG_INSTANCE_STATS not in vrrp_instance:
                    continue
                group: str = vrrp_instance[util.YANG_TAGNODE]
                if filter_grp != "" and int(group) != int(filter_grp):
                    continue
                output += show_detail_group_name(group)
                output += SHOW_DETAIL_GROUP_DIVIDER
                stats: Dict = vrrp_instance[util.YANG_INSTANCE_STATS]
                key: str
                for key in stats:
                    if type(stats[key]) is dict:
                        subkey: str
                        key_name = f"{key}:"
                        output += show_stats_header_format([key_name, ""])
                        for subkey in stats[key]:
                            key_name = f"{subkey}:"
                            output += \
                                show_stats_line_format(
                                    [key_name, stats[key][subkey]])
                        output += "\n"
                    else:
                        key_name = f"{key}:"
                        output += show_stats_header_and_value_format(
                            [key_name, stats[key]])
                        if key == util.SHOW_STATS_RELEASED_MASTER:
                            output += "\n"
    return output


def show_vrrp_statistics_filters(
    stats_dict: Dict,
    filter_intf: str = "",
    filter_grp: str = ""
) -> str:
    """
    Filter function to keep the same output for stats filtering as the legacy
    implementation.

    Arguments:
        stats_dict: a python dictionary containing full statistics information.
        filter_intf: A string to filter the output down to.
        filter_grp:
            A string to filter the output down to
            (must also be called with a filter_intf).
    Returns:
        A string for the "show vrrp statistics interface <intf> group <vrid>"
        call.
    """

    output = show_vrrp_statistics(stats_dict, filter_intf, filter_grp)
    if output == f"\n{SHOW_DETAIL_DIVIDER}":
        output = f"VRRP is not running on {filter_intf}"
    elif output == (f"\n{SHOW_DETAIL_DIVIDER}"
                    f"{show_detail_intf_name(filter_intf)}"
                    f"{SHOW_DETAIL_INTF_DIVIDER}"):
        output = f"No VRRP group {filter_grp} exists on {filter_intf}"
    return output


""" Functions to convert files to JSON"""


def _convert_track_block_to_yang(config_block: List[str]) -> Dict[str, str]:
    """
    Given a list of strings that maps to a single tracked object convert it
    from the list of strings into a yang like dictionary containing only the
    relevant information.

    Arguments:
        config_block: A list of strings denoting a block of tracking config
            e.g.
            ["------< NIC >------", "Name = dp0p1s1 "index = 7",
             "IPv4 address = 10.10.1.2",
             "IPv6 address = fe80::40a0:2ff:fee8:101",
             "MAC = 42:a0:02:e8:01:01", "is UP",
             "is RUNNING", "weight = 10", "MTU = 1500", "HW Type = ETHERNET",
             "Enabling NIC ioctl refresh polling"]
    Returns:
        tracked_obj:
            A Dictionary containing the relevant tracked object information
            e.g.
            {
                "name": "dp0p1s1", "state": "UP",
                "weight": "10"
            }
    """

    tracked_obj: Dict[str, str] = {}
    for line in config_block:
        config_value = line.split()[-1]
        if (util.YANG_NAME.capitalize() in line or
                util.YANG_TRACK_POLICY.capitalize() in line or
                util.DATA_TRACK_ROUTE_NETWORK in line):
            tracked_obj[util.YANG_NAME] = config_value
        elif (util.DATA_TRACK_IS_UP in line or
                util.DATA_TRACK_IS_DOWN in line or
                util.DATA_TRACK_STATUS in line):
            tracked_obj[util.YANG_STATE] = config_value
        elif util.YANG_TRACK_WEIGHT in line or util.DATA_TRACK_WEIGHT in line:
            tracked_obj[util.YANG_TRACK_WEIGHT] = config_value
        elif (util.DATA_TRACK_ROUTE_PREFIX in line and
                util.YANG_NAME in tracked_obj):
            tracked_obj[util.YANG_NAME] = \
                tracked_obj[util.YANG_NAME] + f"/{config_value}"
        if util.YANG_STATE not in tracked_obj:
            tracked_obj[util.YANG_STATE] = util.DATA_TRACK_DOWN
    return tracked_obj


def _convert_tracked_lines_to_yang(
    config_block: List[str],
    start_of_config: int,
    end_of_config: int,
    pathmon: bool = False
) -> List[Any]:
    """
    All tracked objects follow the same config pattern:
        name <object_name> state (UP|DOWN) weight -254..254
    These config lines are marshalled into a list of dictionaries.
    Interface and route tracking dictionary representation are the same
     {
         "name": <object_name>,
         "state": ("UP"|"DOWN"),
         # if weight != 0
         "weight": -254..254
     }
    For path monitor the dictionary representation, and show output, is
    slightly different. There is a one to many relationship between
    monitors and policies, the <object_name> of the tracked object is of
    the form <monitor>/<policy> and is split to generate the names.
     {
         "name": <monitor>
         "policies": [
             {
                 "name": <policy>,
                 "state": ("COMPLIANT"|"NON_COMPLIANT"),
                 # if weight != 0
                 "weight": -254..254
             },
             ...
         ]
     }
    To avoid breaking existing scripts we translate the Keepalived
    tracked state values to the expect show output values:
        "UP"    => "COMPLIANT"
        "DOWN"  => "NON_COMPLIANT"
    """

    tracked_object_list: List[Any] = []
    for line in config_block[start_of_config: end_of_config + 1]:
        config_tokens: List[str] = line.split()
        name_key: str = \
            config_tokens[util.TrackConstant.NAME_KEY.value]
        name: str = \
            config_tokens[util.TrackConstant.NAME_VALUE.value]
        state_key: str = \
            config_tokens[util.TrackConstant.STATE_KEY.value]
        state: str = \
            config_tokens[util.TrackConstant.STATE_VALUE.value]
        weight_key: str = \
            config_tokens[util.TrackConstant.WEIGHT_KEY.value]
        weight: str = \
            config_tokens[util.TrackConstant.WEIGHT_VALUE.value]
        if not pathmon:
            tracked_object: Dict[str, str] = {
                name_key: name,
                state_key: state,
            }
            if weight != "0":
                tracked_object[weight_key] = weight
            tracked_object_list.append(tracked_object)
        else:
            # Preprocessing the pathmon config line, need to find or create
            # the monitor dictionary that the policy dictionaries will be
            # added to.
            pathmon_tokens: List[str] = \
                name.split("/")
            monitor: str = pathmon_tokens[0]
            policy: str = pathmon_tokens[1]
            if len(tracked_object_list) == 0 or \
                    tracked_object_list[-1][name_key] != monitor:
                track_mon: Dict[str, str] = {
                    name_key: monitor,
                    util.SHOW_POLICIES: []
                }
                tracked_object_list.append(track_mon)
            # Last object is guaranteed to be the monitor that this policy
            # is attached to
            tracked_object = tracked_object_list[-1]
            state_translated: str
            if state == "UP":
                state_translated = "COMPLIANT"
            else:
                state_translated = "NON_COMPLIANT"

            # Policy dictionary marshalling
            policy_dict: Dict[str, str] = {
                name_key: policy,
                state_key: state_translated,
            }
            if weight != "0":
                policy_dict[weight_key] = weight
            tracked_object[util.SHOW_POLICIES].append(policy_dict)
    return tracked_object_list


def _convert_keepalived_data_to_yang(
    config_block: List[str], sync: str
) -> Dict:
    """
    Given a list of strings representing the state of a VRRP group convert this
    information into a dictionary to be added to a yang representation.

    Arguments:
        config_block: A list of strings denoting the data for a single VRRP
        group.
        sync: The empty string of the name of the sync-group this VRRP is
        part of.

    Returns:
        instance_dict:
            Formatted values from the data file for a single VRRP group.

    N.B.
    Mapping between data string and dictionary key is done using
    util.find_config_value() that takes the current dictionary value for the
    key and attempts to find that in the list of strings. If it's found the
    value of that data item overwrites the value in the dictionary for that
    key. Tracked objects are their own special cases that are dealt with
    elsewhere in this file.
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
            util.YANG_IPAO: f"{util.SHOW_IPAO.capitalize()}",
            util.YANG_LAST_TRANSITION: util.SHOW_LAST_TRANSITION,
            util.YANG_RFC_INTF: util.DATA_XMIT_DEV,
            util.YANG_STATE: f"{util.YANG_STATE.capitalize()}",
            util.YANG_SYNC_GROUP: sync,
            util.YANG_VERSION: util.DATA_VERSION,
            util.YANG_SRC_IP_STATE: util.DATA_SRC_IP,
            util.YANG_BASE_PRIO: util.DATA_BASE_PRIORITY,
            util.YANG_EFFECTIVE_PRIO: util.DATA_EFFECTIVE_PRIORITY,
            util.YANG_ADVERT_INT_STATE: util.DATA_ADVERT_INT,
            util.YANG_ACCEPT: util.SHOW_ACCEPT.capitalize(),
            util.YANG_PREEMPT: util.SHOW_PREEMPT,
            util.YANG_PREEMPT_DELAY: util.SHOW_PREEMPT_DELAY,
            util.YANG_START_DELAY: util.SHOW_START_DELAY,
            util.YANG_AUTH_TYPE: util.SHOW_AUTH_TYPE.title(),
            util.YANG_MASTER_PRIO_STATE: util.SHOW_MASTER_PRIORITY,
            util.YANG_MASTER_ROUTER_STATE: util.SHOW_MASTER_ROUTER
        }

    # Single line config code
    for key in instance_dict:
        if key == util.YANG_SYNC_GROUP:
            continue
        # Search for each term in the config
        config_exists: Union[List, str]
        try:
            config_exists = \
                util.find_config_value(config_block, instance_dict[key])
        except ValueError:
            if key == util.YANG_AUTH_TYPE:
                instance_dict[key] = None
            else:
                instance_dict[key] = "NOTFOUND"
        else:
            split_line: List[str]
            split_line = config_exists.split()
            value = split_line[1]
            if key == util.YANG_ADVERT_INT_STATE:
                if instance_dict[util.YANG_VERSION] == 2:
                    value = f"{value} sec"
                else:
                    value = f"{value} milli-sec"
            elif (key == util.YANG_START_DELAY or key ==
                    util.YANG_PREEMPT_DELAY):
                value = f"{value} secs"
            elif key == util.YANG_RFC_INTF and value == intf:
                value = ""
            if value.isdigit():
                # Term exists in config and has a numerical value
                instance_dict[key] = int(value)
            elif (value == util.SHOW_IPAO_NO or value ==
                    util.SHOW_PREEMPT_DISABLED):
                instance_dict[key] = False
            elif (value == util.SHOW_IPAO_YES or value ==
                    util.SHOW_PREEMPT_ENABLED):
                instance_dict[key] = True
            else:
                instance_dict[key] = value

    tracked_dict: Dict = {}
    tracked_indexes: List
    tracked_config_end: int

    # Multi line config code
    try:
        util.find_config_value(config_block, util.DATA_TRACK_INTF_COUNT)
    except ValueError:
        pass  # Tracked interface not in configuration
    else:
        num_track_intf: int = int(util.find_config_value(
            config_block, util.DATA_TRACK_INTF_COUNT
        ))
        tracked_indexes = util.get_config_indexes(
            config_block,
            util.DATA_TRACK_INTF_COUNT)
        tracked_config_start = tracked_indexes[0] + 1
        tracked_config_end = tracked_indexes[0] + num_track_intf
        tracked_dict[util.YANG_INTERFACE_CONST] = (
            _convert_tracked_lines_to_yang(config_block,
                                           tracked_config_start,
                                           tracked_config_end))

    try:
        util.find_config_value(config_block, util.DATA_TRACK_PMON_COUNT)
    except ValueError:
        pass  # Tracked path monitor not in configuration
    else:
        num_track_pmons: int = int(util.find_config_value(
            config_block, util.DATA_TRACK_PMON_COUNT
        ))
        tracked_indexes = util.get_config_indexes(
            config_block,
            util.DATA_TRACK_PMON_COUNT)
        tracked_config_start = tracked_indexes[0] + 1
        tracked_config_end = tracked_indexes[0] + num_track_pmons
        tracked_dict[util.YANG_TRACK_MONITOR] = (
            _convert_tracked_lines_to_yang(config_block,
                                           tracked_config_start,
                                           tracked_config_end,
                                           True))

    try:
        util.find_config_value(config_block, util.DATA_TRACK_ROUTES_COUNT)
    except ValueError:
        pass  # Tracked routes not in configuration
    else:
        num_track_routes: int = int(util.find_config_value(
            config_block, util.DATA_TRACK_ROUTES_COUNT
        ))
        tracked_indexes = util.get_config_indexes(
            config_block,
            util.DATA_TRACK_ROUTES_COUNT)
        tracked_config_start = tracked_indexes[0] + 1
        tracked_config_end = tracked_indexes[0] + num_track_routes
        tracked_dict[util.YANG_TRACK_ROUTE] = (
            _convert_tracked_lines_to_yang(config_block,
                                           tracked_config_start,
                                           tracked_config_end))

    if tracked_dict != {}:
        instance_dict[util.YANG_TRACK] = tracked_dict

    vip_tuple: Union[List, str]
    try:
        vip_tuple = util.find_config_value(
            config_block, f"{util.DATA_VIP_COUNT} =")
    except ValueError:
        pass
    else:
        num_vips: int = int(vip_tuple)
        vips_start = util.get_config_indexes(
            config_block, util.DATA_VIP_COUNT)[0]
        vips_end = vips_start + num_vips + 1
        virtual_addresses = []
        for address in config_block[vips_start + 1:vips_end]:
            virtual_addresses.append(address.split()[0])
        instance_dict[util.YANG_VIP_STATE] = virtual_addresses

    instance_dict = \
        {key: val for key, val in instance_dict.items()
         if val != "NOTFOUND"}

    return {util.YANG_INSTANCE_STATE: instance_dict, util.YANG_TAGNODE: vrid}


def convert_data_file_to_dict(data_string: str) -> Dict:
    """
    Convert a string from the data file into the full yang representation
    required for show outputs of "show vrrp detail", "show vrrp interfaces",
    and "show vrrp sync"

    Arguments:
        data_string: A string obtained from /tmp/keepalived.data
    Returns:
        A python dictionary in a similar format to the YANG representation of
        VRRP groups.

    Detailed conversion notes and process.
    From:
    ------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Transmitting device = dp0p1s1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 50
   Effective priority = 70
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Tracked interfaces = 1
------< NIC >------
 Name = dp0p1s1
 index = 7
 IPv4 address = 10.10.1.2
 IPv6 address = fe80::40a0:2ff:fee8:101
 MAC = 42:a0:02:e8:01:01
 is UP
 is RUNNING
 weight = 10
 MTU = 1500
 HW Type = ETHERNET
 Enabling NIC ioctl refresh polling
   Tracked path-monitors = 2
   Monitor = test_monitor
   Policy = test_policy
   Weight = 10
   Status = COMPLIANT
   Monitor = test_monitor
   Policy = test_nonpolicy
   Status = COMPLIANT
   Tracked routes = 1
   Network = 10.10.10.0
   Prefix = 24
   Status = DOWN
   Weight = 10
   Virtual IP = 1
     10.10.1.100/24 dev dp0p1s1 scope global

    To:
        {
        "vyatta-interfaces-v1:interfaces":{
            "vyatta-interfaces-dataplane-v1:dataplane":
                [
                    {
                        "tagnode":"dp0p1s1",
                        "vyatta-vrrp-v1:vrrp": {
                            "start-delay": 0,
                            "vrrp-group":[
                                {
                                    "instance-state":
                                    {
                                        "address-owner": False,
                                        "last-transition": 0,
                                        "rfc-interface": "",
                                        "state": "MASTER",
                                        "sync-group": "",
                                        "version": 2,
                                        "src-ip": "10.10.1.1",
                                        "base-priority": 50,
                                        "effective-priority": 70,
                                        "advert-interval": "2 sec",
                                        "accept": True,
                                        "preempt": True,
                                        "auth-type": None,
                                        "track": {
                                            "interface": [
                                                {
                                                    "name": "dp0p1s1",
                                                    "state": "UP",
                                                    "weight": "10"
                                                }
                                            ],
                                            "monitor": [
                                                {
                                                    "name": "test_monitor",
                                                    "policies": [
                                                        {
                                                            "name":
                                                              "test_policy",
                                                            "state":
                                                              "COMPLIANT",
                                                            "weight": "10"
                                                        },
                                                        {
                                                            "name":
                                                              "test_nonpolicy",
                                                            "state":
                                                              "COMPLIANT",
                                                        }
                                                    ]
                                                }
                                            ],
                                            "route": [
                                                {
                                                    "name": "10.10.10.0/24",
                                                    "state": "DOWN",
                                                    "weight": "10"
                                                }
                                            ]
                                        },
                                        "virtual-ips": [
                                            "10.10.1.100/24"
                                        ]
                                    },
                                    "tagnode": "1"
                                }
                            ]
                        }
                    }
                ]
            }
        }

    This function follows a similar flow as convert_to_vci_format_dict() from
    vyatta/keepalived/config_file.py. Builds up a python dictionary from a
    text file by:
        1) Create a list of strings by splitting the file string on newlines
            (data_list).
        2) Finds every index of "VRRP Instance" in the list of strings
            (config_indexes).
        3) Using these indexes creates List of strings that logically relate
            to a single VRRP group (config_blocks).
        4) Determines if there are any sync-groups in the config by:
            a) Searches for instances of "VRRP Sync Group" in the data_list.
            b) Processes any of these groups adding a dictionary of them to the
               representation for the "show vrrp sync" output.
            c) Stores the name of sync-group in a dictionary with the VRRP
                instance name as the key.
        5) Processes individual blocks of config from config_blocks converting
            them from a list of strings to a dictionary format. If the name of
            the VRRP instance in the config block is found in the sync-group
            dictionary this is passed to the conversion function as well.
        6) Inserts the data dictionary into the yang representation.
        7) Returns the full representation.
    """

    config_indexes: List[int]
    config_blocks: List[List[str]]
    data_list: List[str]

    yang_representation: Dict[str, Dict] = {
        util.INTERFACE_YANG_NAME: {}
    }
    data_list = data_string.split("\n")
    config_indexes = util.get_config_indexes(
        data_list, util.DATA_INSTANCE_START)
    config_blocks = util.get_config_blocks(data_list, config_indexes)

    sync_group_start_indexes: List[int] = util.get_config_indexes(
        data_list, util.DATA_SG_INSTANCE_START)
    sync_group_instances: Dict = {}
    if sync_group_start_indexes != []:
        yang_representation[util.VRRP_YANG_NAME] = \
            {f"{util.YANG_SYNC_GROUP}s": []}
        sync_group_data_list = data_list[sync_group_start_indexes[0]:]
        sync_group_start_indexes = util.get_config_indexes(
            sync_group_data_list, util.DATA_SG_INSTANCE_START)
        sync_group_config: List[str] = util.get_config_blocks(
            sync_group_data_list,
            sync_group_start_indexes
        )

        sync_group: str
        for sync_group in sync_group_config:
            sync_group_show_dict: Dict[str, Union[str, List[str]]] = {}
            group_name_exists: Union[List, str]
            group_tokens: List[str]
            try:
                group_name_exists = \
                    util.find_config_value(
                        sync_group, util.DATA_SG_INSTANCE_START)
            except ValueError:
                continue
            else:
                group_tokens = group_name_exists.split()
            group_name: str = group_tokens[1][:-1]
            sync_group_show_dict[util.YANG_NAME] = group_name
            sync_group_show_dict[util.YANG_STATE] = group_tokens[-1]
            sync_group_show_dict[util.YANG_SG_MEMBER] = []
            for instance in sync_group[1:]:
                if instance == "":
                    continue
                tokens = instance.split()
                sync_group_instances[tokens[-1]] = group_name
                if isinstance(sync_group_show_dict[util.YANG_SG_MEMBER], list):
                    sync_group_show_dict[util.YANG_SG_MEMBER].append(
                        tokens[-1]
                    )
            vrrp_group: Dict = yang_representation[util.VRRP_YANG_NAME]
            vrrp_group[f"{util.YANG_SYNC_GROUP}s"].append(
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
        interface_types: Dict[Any, Any] = \
            yang_representation[util.INTERFACE_YANG_NAME]
        interface_list: List[Dict]
        # Find the interface type for the interface name, right now this
        # is just a guess, there might be a better method of doing this
        # than regexes
        intf_type: str = util.intf_name_to_type(intf_name)[0]
        if intf_type not in interface_types:
            interface_types[intf_type] = []
        interface_list = interface_types[intf_type]

        # Hackery to find the reference to the interface this VRRP
        # group should be added to.
        insertion_point: List[Dict] = util.find_interface_in_yang_repr(
            intf_name, vif_number, interface_list)

        current_vrrp_namespace: str = util.get_namespace(
            insertion_point, util.VRRP_YANG_NAMESPACES
        )
        if current_vrrp_namespace == "":
            continue
        insertion_point[current_vrrp_namespace][util.YANG_VRRP_GROUP].append(
            instance_dict
        )
        if util.YANG_START_DELAY in insertion_point[current_vrrp_namespace]:
            del insertion_point[current_vrrp_namespace][util.YANG_START_DELAY]

    return yang_representation


def _convert_keepalived_stats_to_yang(
    config_block: List[str]
) -> Dict:
    """
    Given a list of strings representing the statistics of a VRRP group
    convert this information into a dictionary to be added to a yang
    representation.

    Arguments:
        config_block: A list of strings denoting the stats for a single
                      VRRP group.

    Returns:
        instance_dict:
            Formatted values from the stats file for a single VRRP group.
    """

    instance_dict: Dict = {}
    key: str
    vrid: str

    if config_block == []:
        return instance_dict

    instance_name = config_block[0].split("-")
    vrid = instance_name[2]

    instance_dict = \
        {
            util.STATS_ADVERT_KEY: {
                util.STATS_RECV_KEY: "",
                util.STATS_SENT_KEY: ""
            },
            util.STATS_BECOME_KEY: "",
            util.STATS_RELEASE_KEY: "",
            util.STATS_PACKET_KEY: {
                util.STATS_LENGTH_KEY: "",
                util.STATS_TTL_KEY: "",
                util.STATS_INVALID_TYPE_KEY: "",
                util.STATS_ADVERT_INTERVAL_KEY: "",
                util.STATS_ADDRESS_LIST_KEY: ""
            },
            util.STATS_AUTH_ERROR_KEY: {
                util.STATS_INVALID_TYPE_KEY: "",
                util.STATS_TYPE_MISMATCH_KEY: "",
                util.STATS_FAILURE_KEY: 0
            },
            util.STATS_PZERO_KEY: {
                util.STATS_RECV_KEY: "",
                util.STATS_SENT_KEY: ""
            }
        }

    # Single line config code
    config_index: int = 0
    value: List[str]
    while config_index < len(config_block):
        line: str = config_block[config_index].casefold()
        if util.STATS_ADVERT_KEY.casefold() in line:
            for key in instance_dict[util.STATS_ADVERT_KEY]:
                config_index += 1
                value = config_block[config_index].split()
                instance_dict[util.STATS_ADVERT_KEY][key] = value[-1]
        elif util.STATS_BECOME_KEY.casefold() in line:
            value = config_block[config_index].split()
            instance_dict[util.STATS_BECOME_KEY] = value[-1]
        elif util.STATS_RELEASE_KEY.casefold() in line:
            value = config_block[config_index].split()
            instance_dict[util.STATS_RELEASE_KEY] = value[-1]
        elif util.STATS_PACKET_KEY.casefold() in line:
            for key in instance_dict[util.STATS_PACKET_KEY]:
                config_index += 1
                value = config_block[config_index].split()
                instance_dict[util.STATS_PACKET_KEY][key] = value[-1]
        elif util.STATS_AUTH_ERROR_KEY.casefold() in line:
            for key in instance_dict[util.STATS_AUTH_ERROR_KEY]:
                config_index += 1
                value = config_block[config_index].split()
                instance_dict[util.STATS_AUTH_ERROR_KEY][key] = value[-1]
        elif util.STATS_PZERO_SEARCH_STR.casefold() in line:
            for key in instance_dict[util.STATS_PZERO_KEY]:
                config_index += 1
                value = config_block[config_index].split()
                instance_dict[util.STATS_PZERO_KEY][key] = value[-1]
        config_index += 1

    return {"stats": instance_dict, util.YANG_TAGNODE: int(vrid)}


def convert_stats_file_to_dict(data_string: str) -> Dict:
    """
    Convert a string from the data file into the full yang representation
    required for show outputs of "show vrrp detail", "show vrrp interfaces",
    and "show vrrp sync"

    Arguments:
        data_string: A string obtained from /tmp/keepalived.data
    Returns:
        A python dictionary in a similar format to the YANG representation of
        VRRP groups.

    Detailed conversion notes and process.
    From:
VRRP Instance: vyatta-dp0p1s1-1
  Advertisements:
    Received: 0
    Sent: 615
  Became master: 1
  Released master: 0
  Packet Errors:
    Length: 0
    TTL: 0
    Invalid Type: 0
    Advertisement Interval: 0
    Address List: 0
  Authentication Errors:
    Invalid Type: 0
    Type Mismatch: 0
    Failure: 0
  Priority Zero:
    Received: 0
    Sent: 0

    To:
        {
        "vyatta-interfaces-v1:interfaces":{
            "vyatta-interfaces-dataplane-v1:dataplane":
                [
                    {
                        "tagnode":"dp0p1s1",
                        "vyatta-vrrp-v1:vrrp": {
                            "vrrp-group":[
                                {
                                    "tagnode": 1,
                                    "stats": {
                                        "Advertisements": {
                                            "Received": "0",
                                            "Sent": "615"
                                        },
                                        "Became master": "1",
                                        "Released master": "0",
                                        "Packet errors": {
                                            "Length": "0",
                                            "TTL": "0",
                                            "Invalid type": "0",
                                            "Advertisement interval": "0",
                                            "Address list": "0"
                                        },
                                        "Authentication errors": {
                                            "Invalid type": "0",
                                            "Type mismatch": "0",
                                            "Failure": "0"
                                        },
                                        "Priority zero advertisements": {
                                            "Received": "0",
                                            "Sent": "0"
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }

    This function follows a similar flow as convert_to_vci_format_dict() from
    vyatta/keepalived/config_file.py. Builds up a python dictionary from a
    text file by:
        1) Create a list of strings by splitting the file string on
            newlines (data_list).
        2) Finds every index of "VRRP Instance" in the list of strings
            (config_indexes).
        3) Using these indexes creates List of strings that logically relate
            to a single VRRP group (config_blocks).
        4) Processes individual blocks of stats from config_blocks converting
            them from a list of strings to a dictionary format.
        5) Inserts the data dictionary into the yang representation.
        6) Returns the full representation.
    """

    data_dict: dict
    config_indexes: List[int]
    config_blocks: List[List[str]]
    data_list: List[str]

    yang_representation: Dict[str, Dict] = {
        util.INTERFACE_YANG_NAME: {}
    }
    data_list = data_string.split("\n")
    config_indexes = util.get_config_indexes(
        data_list, util.DATA_INSTANCE_START)
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
        interface_types: Dict[Any, Any] = \
            yang_representation[util.INTERFACE_YANG_NAME]
        interface_list: List[Dict]
        # Find the interface type for the interface name, right now this
        # is just a guess, there might be a better method of doing this
        # than regexes
        intf_type: str = util.intf_name_to_type(intf_name)[0]
        if intf_type not in interface_types:
            interface_types[intf_type] = []
        interface_list = interface_types[intf_type]

        # Hackery to find the reference to the interface this VRRP
        # group should be added to.
        insertion_point: List[Dict] = util.find_interface_in_yang_repr(
            intf_name, vif_number, interface_list)

        current_vrrp_namespace: str = util.get_namespace(
            insertion_point, util.VRRP_YANG_NAMESPACES
        )
        if current_vrrp_namespace == "":
            continue
        insertion_point[current_vrrp_namespace][util.YANG_VRRP_GROUP].append(
            instance_dict
        )
        if util.YANG_START_DELAY in insertion_point[current_vrrp_namespace]:
            del insertion_point[current_vrrp_namespace][util.YANG_START_DELAY]

    return yang_representation


def show_autocomplete(
    state_dict: Dict,
    filter_intf: str = "",
    filter_sync: str = ""
) -> str:
    """
    List which interfaces, groups on an interface, or sync groups can be used
    to in other show commands for filters.
    """

    output: str = ""
    intf_type: str
    if filter_sync != "":
        if util.VRRP_YANG_NAME in state_dict:
            sync_groups: Dict = state_dict[util.VRRP_YANG_NAME]
            sync_group: Dict
            for sync_group in \
                    sync_groups[f"{util.YANG_SYNC_GROUP}s"]:
                output += f"{sync_group[util.YANG_NAME]}\n"
    elif filter_intf != "":
        state_dict = util.sanitize_vrrp_config(state_dict)
        # Show vrrp groups on this interface
        intf_type: str = util.intf_name_to_type(filter_intf)[0]
        intf: Dict
        intf_list: List = \
            state_dict[util.INTERFACE_YANG_NAME][intf_type]
        for intf in intf_list:
            intf_name_key: str = util.get_namespace(
                intf, util.YANG_INTERFACE_NAMESPACE
            )
            if intf_name_key == "":
                continue
            if intf[intf_name_key] == filter_intf:
                current_vrrp_namespace: str = util.get_namespace(
                    intf, util.VRRP_YANG_NAMESPACES
                )
                if current_vrrp_namespace == "":
                    continue
                vrrp_instances: List = \
                    intf[current_vrrp_namespace][util.YANG_VRRP_GROUP]
                vrrp_instance: Dict
                for vrrp_instance in vrrp_instances:
                    output += f"{vrrp_instance[intf_name_key]}\n"
                break
    else:
        state_dict = util.sanitize_vrrp_config(state_dict)
        for intf_type in state_dict[util.INTERFACE_YANG_NAME]:
            intf_list: List = \
                state_dict[util.INTERFACE_YANG_NAME][intf_type]
            intf: Dict
            for intf in intf_list:
                intf_name_key: str = util.get_namespace(
                    intf, util.YANG_INTERFACE_NAMESPACE
                )
                if intf_name_key == "":
                    continue
                output += f"{intf[intf_name_key]}\n"
    return output
