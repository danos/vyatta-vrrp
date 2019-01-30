#! /usr/bin/python

# **** License ****
# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# 
# SPDX-License-Identifier: GPL-2.0-only
#
# **** End License ****
#

"""
This script is used to get the state of all vrrp groups on a single interface,
it is called from config:get-state under the vrrp yang node.

To retrieve state we need an explicit DBus path of the form:
/org/keepalived/Vrrp1/Instance/<intf_name>/<vrid>/<af_family>
e.g. /org/keepalived/Vrrp1/Instance/dp0p1s1/1/IPv4

To create this path we need to know where in the config tree we've been called.
For the interface name this can be found using the environment the script is
called with CONFIGD_PATH in the env. This gives us the vrrp node from the
yang tree and we can build the interface name from the path.
For the VRID and address family we need to know more about the config on the
box. For this we get the config below vrrp-groups and loop through them.
Calling the DBus object with the tagnode value in the vrrp group and converting
the first VIP in the VRRP config into either IPv4 or IPv6 to finish off the
path.

The DBus structure returned is then marshalled into the expected yang json and
returned to the caller.

NB, this script is written in python2 as the existing python scripts are python2
it will be superseded by a python3 VCI component in the near future.
"""

import os
import sys
import syslog

import json
import pydbus

import vyatta.configd as configd

# DBus constants that are used to query VRRP groups
KEEPALIVED_DBUS_INTF_NAME = "org.keepalived.Vrrp1"
VRRP_INSTANCE_DBUS_INTF_NAME = "org.keepalived.Vrrp1.Instance"
VRRP_INSTANCE_DBUS_PATH = "/org/keepalived/Vrrp1/Instance"
PROPERTIES_DBUS_INTF_NAME = "org.freedesktop.DBus.Properties"

# DBus properties constants
DBUS_FSM_STATE = "State"
DBUS_IPAO_MODE = "AddressOwner"
DBUS_TRANSITION = "LastTransition"
DBUS_RFC_MODE = "XmitIntf"
DBUS_SYNCG_NAME = "SyncGroup"

# Yang node name constants
VRRP = "vrrp"
VRRP_GROUP = "vrrp-group"
NAME = "tagnode"
STATE = "instance-state"
FSM_STATE = "state"
IPAO_MODE = "address-owner"
TRANSITION = "last-transition"
RFC_MODE = "rfc-interface"
SYNCG_NAME = "sync-group"
VIP = "virtual-address"

def debug_log(log_string):
    syslog.syslog(syslog.LOG_DEBUG, log_string)

def error_log(log_string):
    syslog.syslog(syslog.LOG_ERR, log_string)

def info_log(log_string):
    syslog.syslog(syslog.LOG_INFO, log_string)

def get_af_type(vip):
    if "." in vip:
        af_type = "IPv4"
    elif ":" in vip:
        af_type = "IPv6"
    else:
        af_type = None
    return af_type

def get_vrrp_dbus_properties(dbus_path, dbus_connection):
    """
    Query VRRP DBus object for properties
    """

    debug_log("Using DBus path {}\n".format(dbus_path))

    vrrp_group_dbus_proxy = dbus_connection.get(
        KEEPALIVED_DBUS_INTF_NAME,
        dbus_path
    )
    vrrp_property_interface = vrrp_group_dbus_proxy[PROPERTIES_DBUS_INTF_NAME]
    group_dbus_state = vrrp_property_interface.GetAll(
        VRRP_INSTANCE_DBUS_INTF_NAME
    )
    return group_dbus_state

def marshall_dbus_state_for_yang(dbus_state, vrid, intf):
    """
    Convert between dbus property format and yang dictionary format.
    """

    group_state = \
        {
            STATE: {
                FSM_STATE: dbus_state[DBUS_FSM_STATE][1].upper(),
                IPAO_MODE: dbus_state[DBUS_IPAO_MODE][0],
                TRANSITION: dbus_state[DBUS_TRANSITION][0],
            },
            NAME: vrid
        }
    # rfc-interface and sync-group are only returned if the group is in rfc
    # mode, or part of a sync group. Fill in the details here if they
    # should be returned in state information
    if dbus_state[DBUS_RFC_MODE][0] != intf:
            group_state[STATE][RFC_MODE] = dbus_state[DBUS_RFC_MODE][0]
    if dbus_state[DBUS_SYNCG_NAME][0] != "":
            group_state[STATE][SYNCG_NAME] = dbus_state[DBUS_SYNCG_NAME][0]
    return group_state

def get_vrrp_group_state(group, intf, dbus_connection):
    """
    Given an interface and a VRRP group ID return the state information
    for that group in a python dictionary format
    """

    vrid = group[NAME]
    af_type = get_af_type(group[VIP][0])
    if af_type is None:
        error_log("VRRP group {} on {} has an address that isn't IPv4 or IPv6"
                  ", this is an error. Exiting.\n".format(vrid, intf))
        return -1

    # DBus paths can't contain . so replacing them with the legal _
    group_dbus_path = "{}/{}/{}/{}".format(
        VRRP_INSTANCE_DBUS_PATH,
        intf.replace(".", "_"), vrid, af_type
    )
    debug_log(
        "Getting state for group {} on interface {}\n".format(vrid, intf)
    )
    group_dbus_state = get_vrrp_dbus_properties(
        group_dbus_path,
        dbus_connection
    )

    # Return the interface name to it's original format. This is required
    # because rfc mode is defined by the transmitting interface not being the
    # same as the receiving interface.
    group_state = marshall_dbus_state_for_yang(
        group_dbus_state, vrid, intf
    )
    return group_state

def get_interface_name(path):
    """
    Take a yang path and return the interface name. If there is a vif append
    it to the interface name as intf.vif_num
    """

    path_tokens = path.split("/")[1:]
    intf_name = path_tokens[2]
    if "vif" in path_tokens:
        vif_name = path_tokens[path_tokens.index("vif")+1]
        intf_name = "{}.{}".format(intf_name, vif_name)
    return intf_name

def get_vrrp_json_info(intf_name, caller_config):
    """
    Return the state of all vrrp groups on intf_name in the JSON format
    """

    info = {VRRP_GROUP: []}
    bus_object = pydbus.SystemBus()
    for group in caller_config[VRRP][VRRP_GROUP]:
        info[VRRP_GROUP].append(
            get_vrrp_group_state(group, intf_name, bus_object)
        )
    return json.dumps(info)

def get_interface_vrrp_state(path, config):
    """
    Print the state information for all vrrp groups on an interface
    """

    if VRRP_GROUP not in config[VRRP]:
        info_log(
            "VRRP not configured for {}, not getting state\n".format(path)
        )
        return 0
    intf_name = get_interface_name(path)
    info_json = get_vrrp_json_info(intf_name, config)
    debug_log(
        "State dict for interface {} is {}\n".format(
            intf_name, info_json.encode("utf-8")
        )
    )
    # Print out the state inforation for the legacy config system
    print(info_json.encode("utf-8"))
    return 0

def get_interface_config(path):
    """
    Get config under the given path. This is required for VRRP because we use
    the first VIP in the group config to determine what DBus path to query
    """
    client_session = configd.Client()
    config = client_session.tree_get_dict(
        path.replace("/", " "),
        configd.Client.RUNNING, "json"
    )
    return config

def main():
    config_path = os.environ["CONFIGD_PATH"]
    debug_log("VRRP get-state called at node {}\n".format(config_path))
    try:
        caller_config = get_interface_config(config_path)
    except configd.Exception as e:
        error_log("Failed to get config at {}\n".format(config_path))
        error_log("Traceback is {}\n".format(e))
        return {}
    debug_log("The config at this node is {}\n".format(caller_config))
    if VRRP in caller_config:
        get_interface_vrrp_state(config_path, caller_config)
    else:
        error_log(
            "VRRP get-state called at node that doesn't have a vrrp subtree\n"
        )

if __name__ == "__main__":
    main()