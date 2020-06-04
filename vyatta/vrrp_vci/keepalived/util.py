#! /usr/bin/env python3

# Copyright (c) 2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only
"""
Useful functions to be shared between packages. A few have been
moved here from keepalived/config_file.py, they were part of the class
but never actually used anything relating to the class.
"""


import ipaddress
import re
import socket
from enum import Enum
from typing import Any, Dict, Generator, List, Match, Optional, Tuple, Union

# YANG strings for interfaces types, and short names
INTERFACE_YANG_NAME: str = "vyatta-interfaces-v1:interfaces"
DATAPLANE_SHORT_NAME: str = "dataplane"
DATAPLANE_YANG_NAME: str = (
    f"vyatta-interfaces-dataplane-v1:"
    f"{DATAPLANE_SHORT_NAME}")
BONDING_SHORT_NAME: str = "bonding"
BONDING_YANG_NAME: str = f"vyatta-bonding-v1:{BONDING_SHORT_NAME}"
SWITCH_SHORT_NAME: str = "switch"
SWITCH_YANG_NAME: str = f"vyatta-interfaces-switch-v1:{SWITCH_SHORT_NAME}"
VIF_YANG_NAME: str = "vif"

intf_type: Enum = Enum("intf_type", "dataplane bonding switch")

# VRRP YANG keys and namespaces
VRRP_NAMESPACE: str = "vyatta-vrrp-v1"
VRRP: str = "vrrp"
VRRP_YANG_NAME: str = f"{VRRP_NAMESPACE}:{VRRP}"
PATHMON_DATAPLANE_YANG_NAME: str = \
    "vyatta-vrrp-path-monitor-track-interfaces-dataplane-v1:path-monitor"
PATHMON_BONDING_YANG_NAME: str = \
    "vyatta-vrrp-path-monitor-track-interfaces-bonding-v1:path-monitor"
PATHMON_SWITCH_YANG_NAME: str = \
    "vyatta-vrrp-path-monitor-track-interfaces-switch-v1:path-monitor"
ROUTE_DATAPLANE_YANG_NAME: str = \
    "vyatta-vrrp-route-to-track-interfaces-dataplane-v1:route-to"
ROUTE_BONDING_YANG_NAME: str = \
    "vyatta-vrrp-route-to-track-interfaces-bonding-v1:route-to"
ROUTE_SWITCH_YANG_NAME: str = \
    "vyatta-vrrp-route-to-track-interfaces-switch-v1:route-to"

# DBus paths and interfaces for Systemd controls
PROPERTIES_DBUS_INTF_NAME: str = "org.freedesktop.DBus.Properties"
SYSTEMD_DBUS_INTF_NAME: str = "org.freedesktop.systemd1"
SYSTEMD_DBUS_PATH: str = f"/{SYSTEMD_DBUS_INTF_NAME.replace('.', '/')}"
SYSTEMD_MANAGER_DBUS_INTF_NAME: str = f"{SYSTEMD_DBUS_INTF_NAME}.Manager"
SYSTEMD_UNIT_DBUS_NAME: str = f"{SYSTEMD_DBUS_INTF_NAME}.Unit"
SYSTEMD_REPLACE: str = "replace"

# DBus paths and interfaces for VRRP group instance and Keepalived process
KEEPALIVED_DBUS_INTF_NAME: str = "org.keepalived.Vrrp1"
VRRP_PROCESS_DBUS_INTF_PATH: str = \
    f"/{KEEPALIVED_DBUS_INTF_NAME.replace('.', '/')}/Vrrp"
VRRP_INSTANCE_DBUS_INTF_NAME: str = f"{KEEPALIVED_DBUS_INTF_NAME}.Instance"
VRRP_INSTANCE_DBUS_PATH: str = \
    f"/{VRRP_INSTANCE_DBUS_INTF_NAME.replace('.', '/')}"

# Address family string constants
IPV4_AF: str = "IPv4"
IPV6_AF: str = "IPv6"

# DBus property keys
DBUS_IPAO_NAME: str = "AddressOwner"
DBUS_LAST_TRANSITION_NAME: str = "LastTransition"
DBUS_SYNC_GROUP_NAME: str = "SyncGroup"
DBUS_XMIT_INTF_NAME: str = "XmitIntf"

# YANG keys and constants
YANG_INSTANCE_STATE: str = "instance-state"
YANG_TAGNODE: str = "tagnode"
YANG_VRRP_GROUP: str = "vrrp-group"
YANG_INSTANCE_STATS: str = "stats"
YANG_START_DELAY: str = "start-delay"
YANG_VIP: str = "virtual-address"
YANG_RFC: str = "rfc-compatibility"
YANG_RFC_INTF: str = "rfc-interface"
YANG_IPAO: str = "address-owner"
YANG_LAST_TRANSITION: str = "last-transition"
YANG_STATE: str = "state"
YANG_BASE_PRIO: str = "base-priority"
YANG_EFFECTIVE_PRIO: str = "effective-priority"
YANG_HELLO_SOURCE_ADDR: str = "hello-source-address"
YANG_ACCEPT: str = "accept"
YANG_PRIORITY: str = "priority"
YANG_PREEMPT: str = "preempt"
YANG_VERSION: str = "version"
YANG_V2_ADVERT_INT: str = "advertise-interval"
YANG_V3_ADVERT_INT: str = "fast-advertise-interval"
YANG_PREEMPT_DELAY: str = "preempt-delay"
YANG_SYNC_GROUP: str = "sync-group"
YANG_SG_MEMBER: str = "members"
YANG_AUTH: str = "authentication"
YANG_TYPE: str = "type"
YANG_AUTH_TYPE: str = "auth-type"
YANG_AUTH_PASSWORD: str = "password"
YANG_AUTH_PLAINTXT_PASSWORD: str = "plaintext-password"
YANG_AUTH_TYPE_PLAIN: str = "PASS"
YANG_AUTH_TYPE_AH: str = "AH"
YANG_RUN_SCRIPT: str = "run-transition-scripts"
YANG_INTERFACE_CONST: str = "interface"
YANG_TRACK: str = "track"
YANG_TRACK_VALUE: str = "value"
YANG_TRACK_INTERFACE: str = f"{YANG_TRACK}-{YANG_INTERFACE_CONST}"
YANG_TRACK_ROUTE: str = "route"
YANG_TRACK_MONITOR: str = "monitor"
YANG_TRACK_POLICY: str = "policy"
YANG_TRACK_WEIGHT: str = "weight"
YANG_TRACK_INC: str = "increment"
YANG_TRACK_DEC: str = "decrement"
YANG_NAME: str = "name"
YANG_NOTIFY: str = "notify"
YANG_BGP: str = "bgp"
YANG_IPSEC: str = "ipsec"
YANG_INSTANCE: str = "instance"
YANG_DISABLED_GROUP: str = "disable"

# Keys for state dictionaries that don't match config keys
YANG_SRC_IP_STATE: str = "src-ip"
YANG_ADVERT_INT_STATE: str = "advert-interval"
YANG_MASTER_PRIO_STATE: str = "master-priority"
YANG_MASTER_ROUTER_STATE: str = "master-router"
YANG_VIP_STATE: str = "virtual-ips"

# VRRP state strings
STATE_TRANSIENT: str = "TRANSIENT"
STATE_MASTER: str = "MASTER"
STATE_BACKUP: str = "BACKUP"
STATE_FAULT: str = "FAULT"
STATE_INIT: str = "INIT"

# RPC keys
RPC_RFC_MAPPING_RECEIVE: str = f"{VRRP_NAMESPACE}:receive"
RPC_RFC_MAPPING_GROUP: str = f"{VRRP_NAMESPACE}:group"
RPC_GARP_INTERFACE: str = f"{VRRP_NAMESPACE}:{YANG_INTERFACE_CONST}"
RPC_GARP_GROUP: str = f"{VRRP_NAMESPACE}:group"
RPC_RFC_INTERFACE: str = f"{VRRP_NAMESPACE}:transmit"

# Notification name and keys
NOTIFICATION_NAME_YANG: str = "group-state-change"
NOTIFICATION_INSTANCE_NAME: str = f"{VRRP_NAMESPACE}:instance"
NOTIFICATION_NEW_STATE: str = f"{VRRP_NAMESPACE}:new-state"

# Keepalived config keys
CONFIG_ADVERT: str = "adv"
CONFIG_INTF: str = "intf"
CONFIG_DELAY: str = "delay"
CONFIG_VRID: str = "vrid"
CONFIG_VIP: str = "vips"
CONFIG_VMAC: str = "vmac"
CONFIG_PREEMPT_DELAY: str = "preempt_delay"
CONFIG_HELLO_SOURCE_ADDR: str = "mcast_src_ip"
CONFIG_AUTH_PASSWORD: str = "auth_pass"
CONFIG_AUTH_TYPE: str = "auth_type"
CONFIG_VRRP_INSTANCE: str = "vrrp_instance"
CONFIG_VRRP_SYNC_GROUP: str = "vrrp_sync_group"
CONFIG_VRID_FILE: str = "virtual_router_id"
CONFIG_START_DELAY: str = "start_delay"
CONFIG_VRRP_SANITIZED_SYNC_GROUP: str = "sync_group"
CONFIG_VRRP_XMIT_BASE: str = "vmac_xmit_base"
CONFIG_VRRP_ADVERT_INT: str = "advert_int"

# Show detail output constants
SHOW_IPAO_YES: str = "yes"
SHOW_IPAO_NO: str = "no"
SHOW_SG_VALUE: str = "none"
SHOW_PREEMPT_ENABLED: str = "enabled"
SHOW_PREEMPT_DISABLED: str = "disabled"
SHOW_POLICIES: str = "policies"
SHOW_LAST_TRANSITION: str = "Last transition"
SHOW_MASTER_ROUTER: str = "Master router"
SHOW_MASTER_PRIORITY: str = "Master priority"
SHOW_VERSION: str = "Version"
SHOW_RFC_COMPAT: str = "RFC Compliant"
SHOW_VMAC_INTF: str = "Virtual MAC interface"
SHOW_IPAO: str = "Address Owner"
SHOW_SOURCE_ADDR: str = "Source Address"
SHOW_CONFIG_PRIORITY: str = "Configured Priority"
SHOW_EFFECTIVE_PRIORITY: str = "Effective Priority"
SHOW_ADVERT_INT: str = "Advertisement interval"
SHOW_AUTH_TYPE: str = "Authentication type"
SHOW_PREEMPT: str = f"{YANG_PREEMPT.capitalize()}"
SHOW_PREEMPT_DELAY: str = f"{YANG_PREEMPT.capitalize()} delay"
SHOW_START_DELAY: str = "Start delay"
SHOW_ACCEPT: str = f"{YANG_ACCEPT.capitalize()}"
SHOW_SYNC_GROUP: str = f"{YANG_SYNC_GROUP.capitalize()}"
SHOW_TRACK_INTF_COUNT: str = "Tracked Interfaces count"
SHOW_TRACK_PMON_COUNT: str = "Tracked Path Monitor count"
SHOW_TRACK_ROUTES_COUNT: str = "Tracked routes count"
SHOW_VIP_COUNT: str = "VIP count"

# Keepalived data file constants
DATA_XMIT_DEV: str = "Transmitting device"
DATA_VERSION: str = "VRRP Version"
DATA_SRC_IP: str = "Using src_ip"
DATA_BASE_PRIORITY: str = "Base priority"
DATA_EFFECTIVE_PRIORITY: str = "Effective priority"
DATA_ADVERT_INT: str = "Advert interval"
DATA_TRACK_INTF_COUNT: str = "Tracked interfaces ="
DATA_TRACK_PMON_COUNT: str = "Tracked path-monitors ="
DATA_TRACK_ROUTES_COUNT: str = "Tracked routes ="
DATA_TRACK_INTF_DELIMINATOR: str = "------< NIC >------"
DATA_TRACK_ROUTE_NETWORK: str = "Network"
DATA_TRACK_ROUTE_PREFIX: str = "Prefix"
DATA_TRACK_DOWN: str = "DOWN"
DATA_TRACK_IS_UP: str = "is UP"
DATA_TRACK_IS_DOWN: str = f" is {DATA_TRACK_DOWN}"
DATA_TRACK_STATUS: str = "Status"
DATA_TRACK_WEIGHT: str = "Weight"
DATA_TRACK_ENABLE: str = "Enabling"
DATA_VIP_COUNT: str = "Virtual IP"
DATA_INSTANCE_START: str = "VRRP Instance"
DATA_SG_INSTANCE_START: str = "VRRP Sync Group"

# Show stats constants
SHOW_STATS_RELEASED_MASTER: str = "Released master"

# Keepalived stats file constants
STATS_ADVERT_KEY: str = "Advertisements"
STATS_RECV_KEY: str = "Received"
STATS_SENT_KEY: str = "Sent"
STATS_BECOME_KEY: str = "Became master"
STATS_RELEASE_KEY: str = "Released master"
STATS_PACKET_KEY: str = "Packet errors"
STATS_LENGTH_KEY: str = "Length"
STATS_TTL_KEY: str = "TTL"
STATS_INVALID_TYPE_KEY: str = "Invalid type"
STATS_ADVERT_INTERVAL_KEY: str = "Advertisement interval"
STATS_ADDRESS_LIST_KEY: str = "Address list"
STATS_AUTH_ERROR_KEY: str = "Authentication errors"
STATS_TYPE_MISMATCH_KEY: str = "Type mismatch"
STATS_FAILURE_KEY: str = "Failure"
STATS_PZERO_SEARCH_STR: str = "Priority zero"
STATS_PZERO_KEY: str = \
    f"{STATS_PZERO_SEARCH_STR} {STATS_ADVERT_KEY.casefold()}"

# Keepalived debug flags
DEBUG_FLAG_PER_PACKET = 1

# Keepalived file paths
FILE_PATH_KEEPALIVED_DATA = "/tmp/keepalived.data"
FILE_PATH_KEEPALIVED_STATS = "/tmp/keepalived.stats"

# Misc string constants
LOGGING_MODULE_NAME: str = "vyatta-vrrp-vci"
AGENTX_STRING: str = "tcp:localhost:705:1"


def get_specific_vrrp_config_from_yang(
    conf: Dict, value: str
) -> Generator:
    """
    Generator to return the specific config entry from every VRRP group

    Arguments:
        conf (dict):
            A yang representation dict rooted at the top level of the
            tree
        value (str):
            The value key to search each group for
    Example:
        As this is a generator code that uses it should iterate over it
        or create an iterator of the values. What's returned from the
        Generator is a list containing two items:
            1) The value at the specific node
            2) The full path to that node

        list(get_specific_vrrp_config_from_yang(new_config, "priority"))

        for value in get_specific_vrrp_config_from_yang(new_config, "advert"):
            if value[0] < 0:
                print(f"Value at {value[1]} not as expected")
                return False

    Useful if you're checking all of the specific values for something.
    Builds up a path to the node being returned to give useful information
    during the checking phase of commit.
    """
    intf_type: str
    for intf_type in conf[INTERFACE_YANG_NAME]:
        intf: Dict
        # Most interface types contain a namespace and then the interface name,
        # but not all. Vif interfaces have no namespace attached to them so we
        # need to use find() here instead of index() for the vif interface
        # type.
        sanitized_intf_type: str = intf_type[intf_type.find(':') + 1:]
        if sanitized_intf_type == VIF_YANG_NAME:
            sanitized_intf_type = intf_name_to_type(
                conf[INTERFACE_YANG_NAME][intf_type][0][YANG_TAGNODE]
            )[1].name
        yang_root: str = f"interfaces {sanitized_intf_type} "
        for intf in conf[INTERFACE_YANG_NAME][intf_type]:
            if YANG_VRRP_GROUP not in intf[VRRP_YANG_NAME]:
                continue  # start-delay default but no vrrp config
            group: Dict
            for group in intf[VRRP_YANG_NAME][YANG_VRRP_GROUP]:
                if value in group:
                    intf_name: str = intf[YANG_TAGNODE]
                    if "." in intf_name:
                        vif_tokens: List[str] = intf_name.split(".")
                        intf_name = f"{vif_tokens[0]} vif {vif_tokens[1]}"
                    yang_path: str = (
                        yang_root + f"{intf_name} {VRRP} "
                        f"{YANG_VRRP_GROUP} {group[YANG_TAGNODE]} "
                        f"{value} {group[value]}"
                    )
                    yield [group[value], yang_path]


def is_rfc_compat_configured(conf: Dict) -> bool:
    return next(get_specific_vrrp_config_from_yang(conf, YANG_RFC), []) != []


def get_hello_sources(conf: Dict) -> List[List[str]]:
    """
    Get every hello address source instance in the config

    Calls the generic get_every_instance_from_yang function with
    "hello-source-address" as the target
    """
    return list(get_specific_vrrp_config_from_yang(
        conf, YANG_HELLO_SOURCE_ADDR))


def get_ip_version(address_string: str) -> int:
    return ipaddress.ip_address(address_string).version


def vrrp_ipv6_sort(ips: List[str]) -> List[str]:
    link_locals: List[str] = \
        [ip for ip in ips if re.match(r"^(fe80).*", ip.lower())]
    global_addr: List[str] = \
        [ip for ip in ips if re.match(r"^(?!fe80).*", ip.lower())]
    return link_locals + global_addr


def is_local_address(address_string: str) -> bool:
    """
    Runtime check to determine if the address passed to the function
    exists on the box.

    Arguments:
        address_string (str):
            IP address to check exists on the box

    This is a functionally equivalent implementation of the
    is_local_address that is written in perl. To take into account
    addresses that might be assigned by DHCP this function attempts
    to bind the IP address passed to it. If the address is local no
    error will be raised if it isn't an OSError is raised. Which the
    infrastructure will interpret as a validation error
    """

    ipaddr_version: int = get_ip_version(address_string)
    ipaddr_type: socket.AddressFamily
    if ipaddr_version == 4:
        ipaddr_type = socket.AF_INET
    elif ipaddr_version == 6:
        ipaddr_type = socket.AF_INET6
    try:
        with socket.socket(ipaddr_type, socket.SOCK_STREAM) as s:
            s.bind((address_string, 0))
    except OSError:
        return False
    return True


def sanitize_vrrp_config(conf: Dict) -> Dict:
    """
    Simplify the yang structure so that all vif interfaces
    exist in their own list under the "vyatta-interfaces-v1:interfaces"
    key. Makes processing the VRRP groups much easier, as there's no
    deeper interfaces under existing interfaces.

    Arguments:
        conf (Dict):
            The original yang representation of the config which may
            potentially have vif interfaces hanging under other interfaces

    Return:
        The new config representation with all vif interfaces moved to
        an interface type list. The tagnode for the vifs will be modified
        to be the higher interfaces name and the vif name

    Data example:
        Input
        {
            "vyatta-interfaces-v1:interfaces {
                "vyatta-interfaces-dataplane-v1:dataplane: [
                    {
                        "tagnode": "dp0p1s1", "vif":
                        [
                            {"tagnode": "1"}
                        ]
                    }
                ]
            }
        }

        Output
        {
            "vyatta-interfaces-v1:interfaces {
                "vyatta-interfaces-dataplane-v1:dataplane": [
                    {"tagnode": "dp0p1s1"}
                ],
                "vif" : [
                    {"tagnode": "dp0p1s1.1"}
                ]
            }
        }
    """

    intf_dict: Dict = conf[INTERFACE_YANG_NAME]
    new_dict: Dict = {}
    vif_list: List = []
    intf_type: str
    for intf_type in intf_dict:
        new_list: List = []
        intf: Dict
        for count, intf in enumerate(intf_dict[intf_type]):
            if VRRP_YANG_NAME in intf:
                if YANG_VRRP_GROUP in intf[VRRP_YANG_NAME]:
                    new_list.append(intf_dict[intf_type][count])
            if VIF_YANG_NAME in intf:
                vif_intf: Dict
                for vif_intf in intf[VIF_YANG_NAME]:
                    if VRRP_YANG_NAME not in vif_intf:
                        continue
                    if YANG_VRRP_GROUP in vif_intf[VRRP_YANG_NAME]:
                        new_vif: Dict = vif_intf
                        new_vif[YANG_TAGNODE] = \
                            f"{intf[YANG_TAGNODE]}.{vif_intf[YANG_TAGNODE]}"
                        vif_list.append(new_vif)
                del intf[VIF_YANG_NAME]
        if new_list != []:
            new_dict[intf_type] = new_list
    if vif_list != []:
        new_dict[VIF_YANG_NAME] = vif_list
    return {INTERFACE_YANG_NAME: new_dict}


def get_config_indexes(
        config_lines: List[str],
        search_string: str
) -> List[int]:
    """
    Get index for every list entry that matches the provided search string

    Arguments:
        config_lines (List[str]):
            Keepalived config split into lines
        search_string (str):
            The term to search the lines for

    Return:
        A list of integers denoting the index where a value was found

    Example:
        test_list = ["Test", "Value", "Test", "Test", "Stop"]
        index_list = _get_config_indexes(test_list, "Test")
        print(index_list)  # [0, 2, 3]

    This function is used to find the index of each vrrp_instance, but can
    be used to find other indexes. It's useful to know where each group
    in the config starts.
    """

    stripped_lines: List[str] = [x.strip() for x in config_lines]
    config_start_indices: List[int] = [i for i, x in enumerate(stripped_lines)
                                       if search_string in x]
    return config_start_indices


def get_config_blocks(
        config_list: List[str],
        indexes_list: List[int]
) -> List[List[str]]:
    """
        Group lines of vrrp config into logical blocks for easier processing

    Arguments:
        config_list (List[str]):
            Flat list of keepalived config strings
        indexes_list (List[str]):
            List of integers denoting where each individual vrrp config
            block starts in config_list

    Return:
        A list of list where each entry is a logical block of vrrp group
        config
    """

    stripped_list: List[str] = [x.strip() for x in config_list]
    group_list: List[List[str]] = []
    idx: int
    start: int
    for idx, start in enumerate(indexes_list):
        end: Optional[int] = None
        if idx + 1 < len(indexes_list):
            end = indexes_list[idx + 1]
        group_list.append(stripped_list[start:end])
    return group_list


def find_config_value(
        config_list: List[str],
        search_term: str
) -> Union[List, str]:
    """
    Find a config line in a block of config

    Arguments:
        config_list (List[str]):
            All config lines relating to a single vrrp group
        search_term (str):
            The key to look for in the config

    Return:
        Returns either a value for the search string being found
        or raises an error if the value isn't found an Enum that
        can take one of three formats.
        ValueError("Config not found")
        Present but not configured = [None]
        Present and configured = <found string>

    Example:
        config_block = ["vrrp_instance dp0p1s1", "priority 200",
            "use_vmac"]

        _find_config_value(config_block, "preempt")
        # raise ValueError for caller to deal with

        _find_config_value(config_block, "use_vmac")
        # [None]

        _find_config_value(config_block, "priority")
        # "200"
    """

    line: str
    for line in config_list:
        regex_search: Optional[Match[str]] = \
            re.match(fr"^{search_term}(\s+|$|:)", line)
        if regex_search is not None:
            regex_search = re.match(fr"{search_term}\s+(.*)", line)
            if regex_search is not None:
                return regex_search.group(1)
            # Yang JSON representation has single key with no value as
            # <key>: [null]
            return [None]
    raise ValueError(f"Value {search_term} not found in config")


def find_interface_in_yang_repr(
        interface_name: str,
        vif_number: str,
        interface_list: List[Any]
) -> Dict:
    """
    Find the interface that a vrrp group is to be added to based on
    name of interface and any vif number

    Arguments:
        interface_name (str):
            Name of the interface found in the vrrp group config
        vif_number (str):
            Vif number for the interface, this may be ""
        interface_list (List[Any]):
            The list of interfaces for this interface's type (dataplane,
            bonding, switching, etc). The interface's type should be
            found in the caller

    Return:
        The value returned here is a dictionary representing an yang
        interface.
    NB:
        There is a little bit of magic (read hackery) done to achieve the
        return value. This function uses (and possibly abuses) python's
        pass by assignment characteristics, effectively returning a
        reference to a dictionary inside the interface_list passed to the
        function.
        As we don't reassign interface_list inside the function it is a
        shallow copy to the data structure from the caller. It's possible
        to use this to add to that datastructure or point a new variable
        to an item inside that datastructure.
        Using this we create the interface if it doesn't exist in the list
        and then return a reference to the interface to be used to add the
        vrrp group
    """

    interface_level: Any = None
    intf_dict: Dict

    for intf in interface_list:
        # Interface list has entries so we need to loop through them and
        # see if the interface already exists
        if intf[YANG_TAGNODE] == interface_name:
            interface_level = intf
            break
    else:
        # Interface list is empty so create the interface and add it to the
        # list and then return the reference
        intf_dict = {YANG_TAGNODE: interface_name}
        interface_level = intf_dict
        interface_list.append(intf_dict)

    # Deal with vifs here now that we've found the interface it's on
    if vif_number != "":
        vif_dict: Dict
        if VIF_YANG_NAME not in interface_level:
            vif_dict = {YANG_TAGNODE: vif_number}
            interface_level[VIF_YANG_NAME] = [vif_dict]
        else:
            for vif_dict in interface_level[VIF_YANG_NAME]:
                if vif_dict[YANG_TAGNODE] == vif_number:
                    break
            else:
                vif_dict = {YANG_TAGNODE: vif_number}
                interface_level[VIF_YANG_NAME].append(vif_dict)
        interface_level = vif_dict

    if VRRP_YANG_NAME not in interface_level:
        # If there is no vrrp config in the interface yet add the top level
        # dictionary to the interface
        interface_level[VRRP_YANG_NAME] = {YANG_START_DELAY: 0,
                                           YANG_VRRP_GROUP: []}
    return interface_level


def running_on_vmware() -> bool:
    """
    rfc compatibility mode does not work on VMware kit, VSwitches don't like
    macs moving between boxes, so we need something to check if we're running
    on this kit. This functionality replaces the
    scripts/sbin/vyatta-check-rfc-compatibility.py script
    """

    from vyatta import configd
    client: configd.Client = configd.Client()
    version: Dict = client.call_rpc_dict("vyatta-opd-v1", "command",
                                         {"command": "show",
                                          "args": "version"})
    search: Optional[Match[str]] = \
        re.search(r"Hypervisor:\s*(\w+)", version["output"])
    if search is not None and search.group(1) == "VMware":
        return True
    return False


def intf_name_to_type(name: str) -> Tuple[str, Enum]:
    if re.match(r"dp\d+bond\d+", name):
        return (BONDING_YANG_NAME, intf_type.bonding)
    elif re.match(r"sw\d+", name):
        return (SWITCH_YANG_NAME, intf_type.switch)
    elif re.match(r"dp\d+(.*)\d+", name):
        return (DATAPLANE_YANG_NAME, intf_type.dataplane)
    else:
        raise ValueError(
            f"Unrecognised interface type for interface {name}"
        )


def elapsed_time(time_delta: str) -> str:
    seconds: int = int(time_delta)
    time_str: str = ""
    sec_min: int = 60
    sec_hour: int = sec_min * 60
    sec_day: int = sec_hour * 24
    sec_week: int = sec_day * 7

    weeks: int = int(seconds / sec_week)
    if weeks > 0:
        seconds = int(seconds % sec_week)
        time_str += str(weeks) + "w"
    days: int = int(seconds / sec_day)
    if days > 0:
        seconds = int(seconds % sec_day)
        time_str += str(days) + "d"
    hours: int = int(seconds / sec_hour)
    if hours > 0:
        seconds = int(seconds % sec_hour)
        time_str += str(hours) + "h"
    minutes: int = int(seconds / sec_min)
    if minutes > 0:
        seconds = int(seconds % sec_min)
        time_str += str(minutes) + "m"
    time_str += str(seconds) + "s"

    return time_str
