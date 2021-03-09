# Copyright (c) 2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only


import logging
from decimal import Decimal
from typing import Dict, List

import vyatta.vrrp_vci.keepalived.util as util


class VrrpGroup:
    """
    Simple VRRP group representation.

    Used to represent the keepalived config for each individual
    VRRP group.
    """

    def __init__(
            self, name: str, delay: int, group_config: Dict,
            rfc_num: int = -1
    ) -> None:
        """
        Constructor for the class

        Arguments:
            name (str):
                Name of the interface the VRRP group is configured on.
            delay (int):
                Start delay configured for the interface.
            group_config (Dict):
                YANG Dictionary for the group's config.
            rfc_num (int):
                Forms part of the interface created when using RFC mode.
                Default is -1 for when RFC mode is not being used for this
                group.
        """
        self.log: logging.Logger = logging.getLogger(util.LOGGING_MODULE_NAME)
        self.notify_scripts: List[str] = []
        # Default values from existing code required for minimal
        # config
        self._group_config: Dict = group_config
        self._group_config[util.YANG_PRIORITY] = \
            self._group_config.get(util.YANG_PRIORITY, 100)
        if (util.YANG_V2_ADVERT_INT not in self._group_config and
                util.YANG_V3_ADVERT_INT not in self._group_config):
            self._group_config[util.CONFIG_ADVERT] = 1
        elif util.YANG_V2_ADVERT_INT in self._group_config:
            self._group_config[util.CONFIG_ADVERT] = \
                group_config[util.YANG_V2_ADVERT_INT]
            del self._group_config[util.YANG_V2_ADVERT_INT]
        elif util.YANG_V3_ADVERT_INT in self._group_config:
            fast_advertise: Decimal = \
                group_config[util.YANG_V3_ADVERT_INT] / 1000
            if group_config[util.YANG_V3_ADVERT_INT] % 1000 == 0:
                self._group_config[util.CONFIG_ADVERT] = int(fast_advertise)
            else:
                self._group_config[util.CONFIG_ADVERT] = fast_advertise
            del self._group_config[util.YANG_V3_ADVERT_INT]

        # Values outwith the dictionary
        self._group_config[util.CONFIG_INTF] = name
        self._group_config[util.CONFIG_DELAY] = delay
        self._group_config[util.YANG_STATE] = util.VrrpState.BACKUP.name

        # Autogenerated values from minimal config
        self._group_config[util.CONFIG_VRID] = group_config[util.YANG_TAGNODE]
        self._group_config[util.YANG_ACCEPT] = group_config[util.YANG_ACCEPT]

        first_addr = group_config[util.YANG_VIP][0].split("/")[0]
        ip_version = util.get_ip_version(first_addr)
        if ip_version == 4:
            self._group_config[util.CONFIG_VIP] = """
        """.join(sorted(group_config[util.YANG_VIP]))
        else:
            self._group_config[util.CONFIG_VIP] = """
        """.join(util.vrrp_ipv6_sort(group_config[util.YANG_VIP]))
        del self._group_config[util.YANG_VIP]

        # Template required for minimal config
        self._template = """
vrrp_instance {instance} {{
    state {state}
    interface {intf}
    virtual_router_id {tagnode}
    version {version}
    start_delay {delay}
    priority {priority}
    advert_int {adv}
    virtual_ipaddress {{
        {vips}
    }}"""

        if ip_version == 6:
            self._template += "\n    native_ipv6"

        # Optional config
        if self._group_config[util.YANG_ACCEPT]:
            self._template += "\n    accept"

        if not self._group_config[util.YANG_PREEMPT]:
            self._template += "\n    nopreempt"

        if util.YANG_RFC in self._group_config:
            self._group_config[util.CONFIG_VMAC] = f"{name[:3]}vrrp{rfc_num}"
            if len(self._group_config[util.CONFIG_VMAC]) > 15:
                self.log.warning(
                    "generated interface name is longer than 15 characters"
                )
            else:
                self._template += (
                    "\n    use_vmac {vmac}"
                )

        if util.YANG_PREEMPT_DELAY in self._group_config:
            self._group_config[util.CONFIG_PREEMPT_DELAY] = \
                self._group_config[util.YANG_PREEMPT_DELAY]
            del self._group_config[util.YANG_PREEMPT_DELAY]
            self._template += "\n    preempt_delay {preempt_delay}"
            if util.YANG_PREEMPT in self._group_config and \
                    self._group_config[util.YANG_PREEMPT] is False:
                self.log.warning("preempt delay is ignored when preempt=false")

        if util.YANG_HELLO_SOURCE_ADDR in self._group_config:
            self._group_config[util.CONFIG_HELLO_SOURCE_ADDR] = \
                self._group_config[util.YANG_HELLO_SOURCE_ADDR]
            del self._group_config[util.YANG_HELLO_SOURCE_ADDR]
            self._template += "\n    mcast_src_ip {mcast_src_ip}"

        if util.YANG_AUTH in self._group_config:
            self._group_config[util.CONFIG_AUTH_PASSWORD] = \
                self._group_config[util.YANG_AUTH][util.YANG_AUTH_PASSWORD]
            if (self._group_config[util.YANG_AUTH][util.YANG_TYPE] ==
                    util.YANG_AUTH_PLAINTXT_PASSWORD):
                auth_type = util.YANG_AUTH_TYPE_PLAIN
            else:
                auth_type = util.YANG_AUTH_TYPE_AH
            self._group_config[util.CONFIG_AUTH_TYPE] = auth_type
            self._template += (
                "\n    authentication {{"
                "\n        auth_type {auth_type}"
                "\n        auth_pass {auth_pass}"
                "\n    }}"
            )

        track_intf_dict: Dict = self._group_config.get(
            util.YANG_TRACK_INTERFACE)
        if track_intf_dict is not None:
            track_dict: Dict = self._group_config.get(util.YANG_TRACK, {})
            if track_dict != {}:
                if util.YANG_INTERFACE_CONST in track_dict:
                    track_dict[util.YANG_INTERFACE_CONST].append(
                        *self._group_config[util.YANG_TRACK_INTERFACE]
                    )
                else:
                    track_dict[util.YANG_INTERFACE_CONST] = \
                        self._group_config[util.YANG_TRACK_INTERFACE]
            else:
                self._group_config[util.YANG_TRACK] = {
                    util.YANG_INTERFACE_CONST:
                    track_intf_dict
                }
            del self._group_config[util.YANG_TRACK_INTERFACE]

        if util.YANG_TRACK in self._group_config:
            self._generate_track_string(self._group_config[util.YANG_TRACK])

        if util.YANG_NOTIFY in self._group_config:
            self._template += "\n    notify {{"
            if util.YANG_IPSEC in self._group_config[util.YANG_NOTIFY]:
                self._template += f"\n        {util.LEGACY_NOTIFY_IPSEC}"
                self.notify_scripts.append(util.LEGACY_NOTIFY_IPSEC)
            self._template += "\n    }}"

        # TODO: This may need changed to add transition scripts
        # for all the transition scripts not explicitly defined.
        # That is the behaviour of the legacy scripts but I think
        # anything that needs to react to a state change should listen
        # for dbus/yang notifications and react to them.
        # JIRA VRVDR-51429
        if util.YANG_RUN_SCRIPT in self._group_config:
            transition_scripts = self._group_config[util.YANG_RUN_SCRIPT]
            state_string: str = util.VrrpState.MASTER.name.lower()
            if state_string in transition_scripts:
                self._template += (
                    f"\n    notify_master \""
                    f"{transition_scripts[state_string]} "
                    f"{state_string} {name} "
                    f"{self._group_config[util.CONFIG_VRID]}\""
                )
            state_string = util.VrrpState.BACKUP.name.lower()
            if state_string in transition_scripts:
                self._template += (
                    f"\n    notify_backup \""
                    f"{transition_scripts[state_string]} "
                    f"{state_string} {name} "
                    f"{self._group_config[util.CONFIG_VRID]}\""
                )
            state_string = util.VrrpState.FAULT.name.lower()
            if state_string in transition_scripts:
                self._template += (
                    f"\n    notify_fault \""
                    f"{transition_scripts[state_string]} "
                    f"{state_string} {name} "
                    f"{self._group_config[util.CONFIG_VRID]}\""
                )

        self._instance = f"vyatta-{name}-{group_config[util.YANG_TAGNODE]}"
        self._group_config[util.YANG_INSTANCE] = self._instance

        self._template += "\n}}"

    @property
    def instance_name(self) -> str:
        """Name of this group in the config file"""
        return self._instance

    def get_notify_scripts(self) -> List[str]:
        return self.notify_scripts

    def _generate_track_string(self, track_dict) -> None:
        if util.YANG_INTERFACE_CONST in track_dict:
            self._generate_track_interfaces(
                track_dict[util.YANG_INTERFACE_CONST])
        if util.PATHMON_DATAPLANE_YANG_NAME in track_dict:
            self._generate_track_pathmon(
                track_dict[util.PATHMON_DATAPLANE_YANG_NAME])
        if util.PATHMON_BONDING_YANG_NAME in track_dict:
            self._generate_track_pathmon(
                track_dict[util.PATHMON_BONDING_YANG_NAME])
        if util.PATHMON_SWITCH_YANG_NAME in track_dict:
            self._generate_track_pathmon(
                track_dict[util.PATHMON_SWITCH_YANG_NAME])
        if util.ROUTE_DATAPLANE_YANG_NAME in track_dict:
            self._generate_track_route_to(
                track_dict[util.ROUTE_DATAPLANE_YANG_NAME])
        if util.ROUTE_BONDING_YANG_NAME in track_dict:
            self._generate_track_route_to(
                track_dict[util.ROUTE_BONDING_YANG_NAME])
        if util.ROUTE_SWITCH_YANG_NAME in track_dict:
            self._generate_track_route_to(
                track_dict[util.ROUTE_SWITCH_YANG_NAME])

    def _generate_track_interfaces(self, intf_dict) -> None:
        self._template += "\n    track_interface {{"
        for interface in intf_dict:
            if util.YANG_NAME in interface:
                track_string = f"\n        {interface[util.YANG_NAME]}"
            if util.YANG_TAGNODE in interface:
                track_string = f"\n        {interface[util.YANG_TAGNODE]}"
            if util.YANG_TRACK_WEIGHT in interface:
                if (interface[util.YANG_TRACK_WEIGHT][util.YANG_TYPE] ==
                        util.YANG_TRACK_DEC):
                    multiplier = -1
                else:
                    multiplier = 1
                value = multiplier * \
                    interface[util.YANG_TRACK_WEIGHT][util.YANG_TRACK_VALUE]
                track_string += f"   {util.YANG_TRACK_WEIGHT}  {value:+d}"
            self._template += track_string
        self._template += "\n    }}"  # Close interface brace

    def _generate_track_pathmon(self, pathmon_dict) -> None:
        self._template += "\n    track_pathmon {{"
        for monitor in pathmon_dict[util.YANG_TRACK_MONITOR]:
            monitor_name = monitor[util.YANG_NAME]
            for policy in monitor[util.YANG_TRACK_POLICY]:
                track_string = (
                    f"\n        {util.YANG_TRACK_MONITOR} "
                    f"{monitor_name}    "
                    f"{util.YANG_TRACK_POLICY} {policy[util.YANG_NAME]}"
                )
                if util.YANG_TRACK_WEIGHT in policy:
                    if (policy[util.YANG_TRACK_WEIGHT][util.YANG_TYPE] ==
                            util.YANG_TRACK_DEC):
                        multiplier = -1
                    else:
                        multiplier = 1
                    value = multiplier * \
                        policy[util.YANG_TRACK_WEIGHT][util.YANG_TRACK_VALUE]
                    track_string += \
                        f"      {util.YANG_TRACK_WEIGHT}  {value:+d}"
                self._template += track_string
        self._template += "\n    }}"  # Close pathmon brace

    def _generate_track_route_to(self, route_dict) -> None:
        self._template += "\n    track_route_to {{"
        for route in route_dict:
            if util.YANG_TRACK_ROUTE in route:
                track_string = f"\n        {route[util.YANG_TRACK_ROUTE]}"
            if util.YANG_TRACK_WEIGHT in route:
                if (route[util.YANG_TRACK_WEIGHT][util.YANG_TYPE] ==
                        util.YANG_TRACK_DEC):
                    multiplier = -1
                else:
                    multiplier = 1
                value = multiplier * \
                    route[util.YANG_TRACK_WEIGHT][util.YANG_TRACK_VALUE]
                track_string += f"   {util.YANG_TRACK_WEIGHT}  {value:+d}"
            self._template += track_string
        self._template += "\n    }}"  # Close route brace

    def __repr__(self) -> str:
        return self._template.format(
            **self._group_config
        )
