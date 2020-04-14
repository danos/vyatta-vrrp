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
import socket
import re
from enum import Enum
from typing import List, Union, Tuple, Any, Dict, Generator, Optional, Match

INTERFACE_YANG_NAME: str = "vyatta-interfaces-v1:interfaces"
DATAPLANE_YANG_NAME: str = "vyatta-interfaces-dataplane-v1:dataplane"
BONDING_YANG_NAME: str = "vyatta-bonding-v1:bonding"
SWITCH_YANG_NAME: str = "vyatta-interfaces-switch-v1:switch"

intf_type: Enum = Enum("intf_type", "dataplane bonding switch")

VRRP_YANG_NAME: str = "vyatta-vrrp-v1:vrrp"
VIF_YANG_NAME: str = "vif"
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

PROPERTIES_DBUS_INTF_NAME: str = "org.freedesktop.DBus.Properties"
SYSTEMD_DBUS_INTF_NAME: str = "org.freedesktop.systemd1"
SYSTEMD_DBUS_PATH: str = f"/{SYSTEMD_DBUS_INTF_NAME.replace('.', '/')}"
SYSTEMD_MANAGER_DBUS_INTF_NAME: str = f"{SYSTEMD_DBUS_INTF_NAME}.Manager"
SYSTEMD_UNIT_DBUS_NAME: str = f"{SYSTEMD_DBUS_INTF_NAME}.Unit"

KEEPALIVED_DBUS_INTF_NAME: str = "org.keepalived.Vrrp1"
VRRP_PROCESS_DBUS_INTF_PATH: str = \
    f"/{KEEPALIVED_DBUS_INTF_NAME.replace('.', '/')}/Vrrp"
VRRP_INSTANCE_DBUS_INTF_NAME: str = f"{KEEPALIVED_DBUS_INTF_NAME}.Instance"
VRRP_INSTANCE_DBUS_PATH: str = f"/{VRRP_INSTANCE_DBUS_INTF_NAME.replace('.', '/')}"


INSTANCE_STATE_YANG: str = "instance-state"
TAGNODE_YANG: str = "tagnode"
VRRP_GROUP_YANG: str = "vrrp-group"
INSTANCE_STATS_YANG: str = "stats"


def get_specific_vrrp_config_from_yang(
        conf: Dict, value: str) -> Generator:
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
        or create an iterator of the values.

        list(get_specific_vrrp_config_from_yang(new_config, "priority"))

        for value in get_specific_vrrp_config_from_yang(new_config, "advert"):
            if value < 0:
                return False

    Useful if you're checking all of the specific values for something.
    No indication of which group the config comes from. If there's three
    groups two with the specific config and one with out only two values
    will be yielded to the caller
    """
    intf_type: str
    for intf_type in conf[INTERFACE_YANG_NAME]:
        intf: Dict
        for intf in conf[INTERFACE_YANG_NAME][intf_type]:
            if "vrrp-group" not in intf[VRRP_YANG_NAME]:
                continue  # start-delay default but no vrrp config
            group: Dict
            for group in intf[VRRP_YANG_NAME]["vrrp-group"]:
                if value in group:
                    yield group[value]


def is_rfc_compat_configured(conf: Dict) -> bool:
    conf_exists = list(
                        get_specific_vrrp_config_from_yang(
                            conf, "rfc-compatibility"))
    if conf_exists != []:
        return True
    return False


def get_hello_sources(conf: Dict) -> List[str]:
    """
    Get every hello address source instance in the config

    Calls the generic get_every_instance_from_yang function with
    "hello-source-address" as the target
    """
    return list(get_specific_vrrp_config_from_yang(
                    conf, "hello-source-address"))


def what_ip_version(address_string: str) -> int:
    ipaddr: Union[ipaddress.IPv4Address, ipaddress.IPv6Address] = \
        ipaddress.ip_address(address_string)
    return ipaddr.version


def vrrp_ipv6_sort(ips: List[str]) -> List[str]:
    link_locals: List[str] = \
        [ip for ip in ips if re.match(r"^(fe80).*", ip.lower())]
    global_addr: List[str] = \
        [ip for ip in ips if re.match(r"^(?!fe80).*", ip.lower())]
    return link_locals + global_addr


def is_local_address(address_string: str) -> None:
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

    ipaddr_version: int = what_ip_version(address_string)
    ipaddr_type: socket.AddressFamily
    if ipaddr_version == 4:
        ipaddr_type = socket.AF_INET
    elif ipaddr_version == 6:
        ipaddr_type = socket.AF_INET6
    else:
        raise TypeError(f"{address_string} is not an IPv4 or IPv6 address")
    with socket.socket(ipaddr_type, socket.SOCK_STREAM) as s:
        s.bind((address_string, 0))


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
        count: int = 0
        intf: Dict
        for intf in intf_dict[intf_type]:
            if "vrrp-group" in intf[VRRP_YANG_NAME]:
                new_list.append(intf_dict[intf_type][count])
            count += 1
            if "vif" in intf:
                vif_intf: Dict
                for vif_intf in intf["vif"]:
                    if "vrrp-group" in vif_intf[VRRP_YANG_NAME]:
                        new_vif: Dict = vif_intf
                        new_vif["tagnode"] = \
                            f"{intf['tagnode']}.{vif_intf['tagnode']}"
                        vif_list.append(new_vif)
                del intf["vif"]
        if new_list != []:
            new_dict[intf_type] = new_list
    if vif_list != []:
        new_dict["vif"] = vif_list
    return {INTERFACE_YANG_NAME: new_dict}


def get_config_indexes(
        config_lines: List[str],
        search_string: str) -> List[int]:
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
        indexes_list: List[int]) -> List[List[str]]:
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
        if idx+1 < len(indexes_list):
            end = indexes_list[idx+1]
        group_list.append(stripped_list[start:end])
    return group_list


def find_config_value(
        config_list: List[str],
        search_term: str) -> Tuple[bool, Union[List[None], str]]:
    """
    Find a config line in a block of config

    Arguments:
        config_list (List[str]):
            All config lines relating to a single vrrp group
        search_term (str):
            The key to look for in the config

    Return:
        Returns a tuple that can take one of three formats. The first value
        in the tuple is always a boolean. True for if the search term was
        found in the config, false and a value of "NOTFOUND" as the second
        element otherwise.
        The second value is either [None] if the search term is a presence
        indicator or the value found on the line if the search term is a
        key with configuration

    Example:
        config_block = ["vrrp_instance dp0p1s1", "priority 200",
            "use_vmac"]
        _find_config_value(config_block, "preempt")  # (False, "NOTFOUND")
        _find_config_value(config_block, "use_vmac")  # (True, [None])
        _find_config_value(config_block, "priority")  # (True, "200")
    """

    line: str
    for line in config_list:
        regex_search: Optional[Match[str]] = \
            re.match(f"^{search_term}(\s+|$|:)", line)
        if regex_search is not None:
            regex_search = re.match(f"{search_term}\s+(.*)", line)
            if regex_search is not None:
                return (True, regex_search.group(1))
            # Yang JSON representation has single key with no value as
            # <key>: [null]
            return (True, [None])
    return (False, "NOTFOUND")


def find_interface_in_yang_repr(
        interface_name: str,
        vif_number: str,
        interface_list: List[Any]) -> Dict:
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
    intf_dict: Any = None

    # TODO: This may be better split into two functions, one for interfaces
    # and another for vifs
    if interface_list == []:
        # Interface list is empty so create the interface and add it to the
        # list and then return the reference
        intf_dict = {"tagnode": interface_name}
        interface_level = intf_dict
        interface_list.append(intf_dict)
    else:
        # Interface list has entries so we need to loop through them and
        # see if the interface already exists
        intf: Dict
        for intf in interface_list:
            if intf["tagnode"] == interface_name:
                interface_level = intf
                break

    if interface_level is None:
        # Interface doesn't exists yet but there are interfaces in the list
        # so create the interface and return the reference
        intf_dict = {"tagnode": interface_name}
        interface_list.append(intf_dict)
        interface_level = interface_list[-1]

    # Deal with vifs here now that we've found the interface it's on
    if vif_number != "":
        if VIF_YANG_NAME not in interface_level:
            vif_dict: Dict = {"tagnode": vif_number}
            interface_level[VIF_YANG_NAME] = [vif_dict]
            interface_level = vif_dict
        else:
            vif_exists: bool = False
            vif: Dict
            for vif in interface_level[VIF_YANG_NAME]:
                if vif["tagnode"] == vif_number:
                    vif_exists = True
                    interface_level = vif
                    break
            if not vif_exists:
                vif_dict = {"tagnode": vif_number}
                interface_level[VIF_YANG_NAME].append(vif_dict)
                interface_level = vif_dict

    if VRRP_YANG_NAME not in interface_level:
        # If there is no vrrp config in the interface yet add the top level
        # dictionary to the interface
        interface_level[VRRP_YANG_NAME] = {"start-delay": 0,
                                           "vrrp-group": []}
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
                                   {"command": "show", "args": "version"})
    search: Optional[Match[str]] = \
        re.match(r'Hypervisor:\s*(\w+)', version['output'])
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
