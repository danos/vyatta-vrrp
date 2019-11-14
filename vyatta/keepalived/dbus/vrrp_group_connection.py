#! /usr/bin/env python3

"""
Vyatta VCI component to configure keepalived to provide VRRP functionality
"""

# Copyright (c) 2019 by AT&T, Inc.
# All rights reserved.

import logging
from functools import wraps
from typing import Any, Dict
import vci
import vyatta.keepalived.util as util


def activate_connection(func):
    @wraps(func)
    def wrapper(inst, *args, **kwargs):
        if not inst._activated:
            inst.log.info("Activating object because %s became active",
                          util.KEEPALIVED_DBUS_INTF_NAME)
            inst.vrrp_group_proxy = inst.bus_object.get(
                util.KEEPALIVED_DBUS_INTF_NAME,
                inst.dbus_path
            )
            inst.vrrp_property_interface =\
                inst.vrrp_group_proxy[util.PROPERTIES_DBUS_INTF_NAME]
            group_state = inst.vrrp_property_interface.GetAll(
                util.VRRP_INSTANCE_DBUS_INTF_NAME
            )
            inst.current_state = group_state["State"][1].upper()
            inst._activated = True
        return func(inst, *args, **kwargs)
    return wrapper


class VrrpConnection:

    def __init__(
            self, intf: str, vrid: str, af_type: str, bus_object: Any,
            notify_bgp: bool = None, notify_ipsec: bool = None,
            script_master: bool = None, script_backup: bool = None,
            script_fault: bool = None):
        self.intf = intf
        self.vrid = vrid
        self.bus_object = bus_object
        self.log = logging.getLogger("vyatta-vrrp-vci")
        self.current_state = ""  # type: str
        self.client = vci.Client()
        if af_type == 4:
            self.af_type_str = "IPv4"
        else:
            self.af_type_str = "IPv6"
        self.instance_name = f"vyatta-{self.intf}-{self.vrid}"
        self.dbus_path = f"{util.VRRP_INSTANCE_DBUS_PATH}/{intf}/{vrid}/{self.af_type_str}"
        self.bus_object.watch_name(
            util.KEEPALIVED_DBUS_INTF_NAME,
            name_appeared=activate_connection
        )
        self._activated = False
        self.vrrp_property_interface = None
        self.vrrp_group_proxy = None

    @activate_connection
    def get_instance_state(self) -> Dict:
        if self.vrrp_property_interface is None:
            return {}
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
                "tagnode": f"{self.vrid}"
            }
        return processed_state

    @activate_connection
    def garp(self) -> Dict:
        if self.vrrp_group_proxy is None:
            return {}
        self.vrrp_group_proxy.SendGarp()
        return {}

    @staticmethod
    def state_int_to_string(state):
        if state == 0:
            return "INIT"
        elif state == 1:
            return "BACKUP"
        elif state == 2:
            return "MASTER"
        elif state == 3:
            return "FAULT"
        else:
            return "TRANSIENT"

    def state_change(self, status):
        status_str = self.state_int_to_string(status)
        # May need to also send 5 gARP replies on a master transition
        # there's a note about this in the legacy implementation
        if self.current_state == status_str:
            # No actual state change so do not emit notification
            return
        self.current_state = status_str
        self.log.debug(
            "%s changed state to %s",
            self.instance_name, status_str
        )
        self.client.emit(
            "vyatta-vrrp-v1",
            "group-state-change",
            {
                "vyatta-vrrp-v1:instance": self.instance_name,
                "vyatta-vrrp-v1:new-state": status_str
            }
        )

    @activate_connection
    def subscribe_instance_signals(self) -> None:
        self.log.debug("%s subscribing to signals", self.dbus_path)
        if self.vrrp_group_proxy is None:
            return
        self.vrrp_group_proxy.VrrpStatusChange.connect(
            self.state_change
        )
