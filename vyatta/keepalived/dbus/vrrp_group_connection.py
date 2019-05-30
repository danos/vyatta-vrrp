#! /usr/bin/env python3

"""
Vyatta VCI component to configure keepalived to provide VRRP functionality
"""

# Copyright (c) 2019 by AT&T, Inc.
# All rights reserved.

import vyatta.keepalived.util as util
from typing import Any


def get_instance_state(
        intf: str, vrid: str, af_type: str, bus_object: Any):
    if af_type == 4:
        af_type_str = "IPv4"
    else:
        af_type_str = "IPv6"
    dbus_path = "{}/{}/{}/{}".format(
        util.VRRP_INSTANCE_DBUS_PATH, intf, vrid, af_type_str
    )
    vrrp_group_proxy = bus_object.get(
        util.KEEPALIVED_DBUS_INTF_NAME,
        dbus_path
    )
    vrrp_property_interface =\
        vrrp_group_proxy[util.PROPERTIES_DBUS_INTF_NAME]
    group_state = vrrp_property_interface.GetAll(
        util.VRRP_INSTANCE_DBUS_INTF_NAME
    )
    rfc_intf = ""
    if group_state["XmitIntf"][0] != intf:
        rfc_intf = group_state["XmitIntf"][0]
    processed_state = \
        {
            "instance-state":
            {
                "address-owner": group_state["AddressOwner"][0],
                "last-transition": group_state["LastTransition"][0],
                "rfc-interface": rfc_intf,
                "state": group_state["State"][1].upper(),
                "sync-group": group_state["SyncGroup"][0]
            },
            "tagnode": "{}".format(vrid)}
    return processed_state


def garp(intf: str, vrid: str, bus_object: Any):
    dbus_path = "{}/{}/{}/{}".format(
        util.VRRP_INSTANCE_DBUS_PATH, intf, vrid, "IPv4"
    )  # type: str
    vrrp_group_proxy = bus_object.get(
        util.KEEPALIVED_DBUS_INTF_NAME,
        dbus_path
    )  # type: Any
    vrrp_group_proxy.SendGarp()
    return {}


def find_recv_intf(intf: str, bus_object: Any):
    dbus_path = util.VRRP_PROCESS_DBUS_INTF_PATH  # type: str
    vrrp_process_proxy = bus_object.get(
        util.KEEPALIVED_DBUS_INTF_NAME,
        dbus_path
    )  # type: Any
    return {
        "vyatta-vrrp-v1:receive":
        vrrp_process_proxy.FindRecvIntf(intf)}
