#! /usr/bin/env python3

"""
Vyatta VCI component to configure keepalived to provide VRRP functionality
"""

# Copyright (c) 2020 by AT&T, Inc.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import logging
from functools import wraps
from typing import Any, Callable, Dict, Union

import pydbus

import vci

import vyatta.vrrp_vci.keepalived.util as util


def activate_connection(func) -> Callable:
    @wraps(func)
    def wrapper(inst: "VrrpConnection", *args, **kwargs) -> Callable:
        if not inst._activated:
            # Prints to console when using template scripts, hiding just now
            # inst.log.info(
            #       "Activating object because " +\
            #       f"{util.KEEPALIVED_DBUS_INTF_NAME} became active")
            inst.vrrp_group_proxy = inst.bus_object.get(
                util.KEEPALIVED_DBUS_INTF_NAME,
                inst.dbus_path
            )
            inst.vrrp_property_interface =\
                inst.vrrp_group_proxy[util.PROPERTIES_DBUS_INTF_NAME]
            group_state = inst.vrrp_property_interface.GetAll(
                util.VRRP_INSTANCE_DBUS_INTF_NAME
            )
            inst.current_state = \
                group_state[util.YANG_STATE.capitalize()][1].upper()
            inst._activated = True
        return func(inst, *args, **kwargs)
    return wrapper


class VrrpConnection:

    def __init__(
            self, intf: str, vrid: str, af_type: int,
            bus_object: Any
    ) -> None:
        """
        This object represents the DBus interface/object to a VRRP group.
        """

        if "." in intf:
            intf = intf.replace(".", "_")
        self.intf: str = intf
        self.vrid: str = vrid
        self.bus_object: pydbus.Bus = bus_object
        self.log: logging.Logger = logging.getLogger(util.LOGGING_MODULE_NAME)
        self.current_state: str
        self.client: vci.Client = vci.Client()
        self.af_type_str: str
        if af_type == 4:
            self.af_type_str = util.IPV4_AF
        else:
            self.af_type_str = util.IPV6_AF
        self.instance_name: str = f"vyatta-{self.intf}-{self.vrid}"
        self.dbus_path: str = \
            f"{util.VRRP_INSTANCE_DBUS_PATH}/{intf}/{vrid}/{self.af_type_str}"
        self.bus_object.watch_name(
            util.KEEPALIVED_DBUS_INTF_NAME,
            name_appeared=activate_connection
        )
        self._activated: bool = False
        self.vrrp_property_interface: pydbus.interface = None
        self.vrrp_group_proxy: pydbus.ProxyObject = None

    @activate_connection
    def get_instance_state(self) -> Dict[str, Union[str, Dict[str, str]]]:
        """
        Query the group for the values of it's properties, as defined in the
        Dbus interface and represented in the VRRP State yang.
        """

        if self.vrrp_property_interface is None:
            return {}
        group_state: Dict = self.vrrp_property_interface.GetAll(
            util.VRRP_INSTANCE_DBUS_INTF_NAME
        )
        rfc_intf: str = group_state[util.DBUS_XMIT_INTF_NAME][0]
        if rfc_intf.replace(".", "_") == self.intf:
            rfc_intf = ""
        processed_state: Dict[str, Union[str, Dict[str, str]]] = \
            {
                util.YANG_INSTANCE_STATE:
                {
                    util.YANG_IPAO: group_state[util.DBUS_IPAO_NAME][0],
                    util.YANG_LAST_TRANSITION:
                        group_state[util.DBUS_LAST_TRANSITION_NAME][0],
                    util.YANG_RFC_INTF: rfc_intf,
                    util.YANG_STATE:
                        group_state[util.YANG_STATE.capitalize()][1].upper(),
                    util.YANG_SYNC_GROUP:
                        group_state[util.DBUS_SYNC_GROUP_NAME][0]
                },
                util.YANG_TAGNODE: f"{self.vrid}"
        }
        return processed_state

    @activate_connection
    def garp(self) -> Dict:
        """
        Trigger the group to send a gARP packet to refresh L2 ARP tables.
        """

        if self.vrrp_group_proxy is None:
            return {}
        self.vrrp_group_proxy.SendGarp()
        return {}

    @staticmethod
    def state_int_to_string(state: int) -> str:
        """
        Convert from integer states values to human readable states
        """

        if state == 0:
            return util.STATE_INIT
        elif state == 1:
            return util.STATE_BACKUP
        elif state == 2:
            return util.STATE_MASTER
        elif state == 3:
            return util.STATE_FAULT
        else:
            return util.STATE_TRANSIENT

    def state_change(self, status: int) -> None:
        """
        Call back for when the state change signal fires from the
        DBus object.
        """

        status_str: str = self.state_int_to_string(status)
        # May need to also send 5 gARP replies on a master transition
        # there's a note about this in the legacy implementation
        if self.current_state == status_str:
            # No actual state change so do not emit notification
            return
        self.current_state = status_str
        self.log.debug(
            f"{self.instance_name} changed state to {status_str}"
        )
        self.client.emit(
            {util.VRRP_NAMESPACE},
            util.NOTIFICATION_NAME_YANG,
            {
                util.NOTIFICATION_INSTANCE_NAME: self.instance_name,
                util.NOTIFICATION_NEW_STATE: status_str
            }
        )

    @activate_connection
    def subscribe_instance_signals(self) -> None:
        """
        Register the state change call back
        """

        self.log.debug(f"{self.dbus_path} subscribing to signals")
        if self.vrrp_group_proxy is None:
            return
        self.vrrp_group_proxy.VrrpStatusChange.connect(
            self.state_change
        )

    @activate_connection
    def reset_group_state(self) -> None:
        """
        Reset the VRRP group state to BACKUP
        """

        self.log.info(f"Resetting state of {self.instance_name} to BACKUP", )
        if self.vrrp_group_proxy is None:
            self.log.warn(
                f"Failed to reset state of {self.instance_name}, " +
                f"DBus connection not initialised?")
            return
        group_state: Dict = self.vrrp_property_interface.GetAll(
            util.VRRP_INSTANCE_DBUS_INTF_NAME
        )
        state: str = group_state[util.YANG_STATE.capitalize()][1].upper()
        if state == util.STATE_MASTER:
            self.vrrp_group_proxy.ResetMaster()
        else:
            print(
                f"VRRP group {self.vrid} on {self.intf} is already in BACKUP"
            )
