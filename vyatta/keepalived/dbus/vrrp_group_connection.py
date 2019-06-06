#! /usr/bin/env python3

"""
Vyatta VCI component to configure keepalived to provide VRRP functionality
"""

# Copyright (c) 2019 by AT&T, Inc.
# All rights reserved.

import logging
import vyatta.keepalived.util as util
from typing import Any, Dict


class VrrpConnection:

    def __init__(
            self, intf: str, vrid: str, af_type: str, bus_object: Any):
        self.intf = intf
        self.vrid = vrid
        self.bus_object = bus_object
        self.log = logging.getLogger("vyatta-vrrp-vci")
        if af_type == 4:
            self.af_type_str = "IPv4"
        else:
            self.af_type_str = "IPv6"
        self.dbus_path = "{}/{}/{}/{}".format(
            util.VRRP_INSTANCE_DBUS_PATH, intf, vrid, self.af_type_str
        )
        self.bus_object.watch_name(
            util.KEEPALIVED_DBUS_INTF_NAME,
            name_appeared=self.activate_connection
        )
        self._activated = False

    def activate_connection(self, name):
        self.log.info("Activating object because %s became active",
            name)
        self.vrrp_group_proxy = self.bus_object.get(
            name,
            self.dbus_path
        )
        self.vrrp_property_interface =\
            self.vrrp_group_proxy[util.PROPERTIES_DBUS_INTF_NAME]
        self._activated = True

    def get_instance_state(self) -> Dict:
        if not self._activated:
            self.activate_connection(util.KEEPALIVED_DBUS_INTF_NAME)
        group_state = self.vrrp_property_interface.GetAll(
            util.VRRP_INSTANCE_DBUS_INTF_NAME
        )
        rfc_intf = ""
        if group_state["XmitIntf"][0] != self.intf:
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
                "tagnode": "{}".format(self.vrid)
            }
        return processed_state

    def garp(self) -> Dict:
        if not self._activated:
            self.activate_connection(util.KEEPALIVED_DBUS_INTF_NAME)
        self.vrrp_group_proxy.SendGarp()
        return {}
