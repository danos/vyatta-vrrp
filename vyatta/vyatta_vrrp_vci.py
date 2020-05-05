#! /usr/bin/python3

# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import json
import logging
import pydbus
from typing import Dict, List, Any

import vci  # pylint: disable=import-error
import vyatta.abstract_vrrp_classes as AbstractVrrpConfig
import vyatta.keepalived.util as util
import vyatta.keepalived.dbus.process_control as process_control
import vyatta.keepalived.dbus.vrrp_group_connection as \
    vrrp_dbus


def send_garp(rpc_input: Dict[str, str]) -> Dict:
    intf:str = rpc_input["vyatta-vrrp-v1:interface"]
    group:str = str(rpc_input["vyatta-vrrp-v1:group"])
    vrrp_conn = vrrp_dbus.VrrpConnection(
        intf, group, 4, pydbus.SystemBus()
    )
    vrrp_conn.garp()
    return {}


class Config(vci.Config):

    # Class attributes that will be the same across all instances
    def __init__(self, config_impl):
        super().__init__()
        self._conf_obj = config_impl
        if not isinstance(self._conf_obj, AbstractVrrpConfig.ConfigFile):
            raise TypeError("Implementation of config object does not "
                            "inherit from abstract class, developer needs "
                            "to fix this ")
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        self.log = logging.getLogger("vyatta-vrrp-vci")
        self.pc = process_control.ProcessControl()

    def set(self, conf: Dict[str, Any]) -> None:
        conf = util.sanitize_vrrp_config(conf)

        # If all the default config has been removed and
        # there's nothing left in the interfaces dictionary
        # just return as we have nothing left to do
        if {} == conf[util.INTERFACE_YANG_NAME]:
            if self.pc.is_running():
                self.pc.shutdown_process()
                self._conf_obj.shutdown()
            return
        self.log.debug(
            "Got following config from VCI infra:%s",
            json.dumps(conf, indent=4, sort_keys=True))

        self._conf_obj.update(conf)
        self._conf_obj.write_config()
        if self.pc.is_running():
            self.pc.reload_process_config()
        else:
            self.pc.start_process()
        self.log.info(
            "%s config written to %s",
            self._conf_obj.impl_name(),
            self._conf_obj.config_file_path()
        )
        return

    def get(self) -> Dict[str, Any]:
        file_config: str = self._conf_obj.read_config()
        yang_repr: Dict[str, Any] = self._conf_obj.convert_to_vci_format(file_config)
        self.log.info(
            "%s yang repr returned to vci infra",
            yang_repr
        )
        return yang_repr

    def check(self, conf: Dict[str, Any]) -> None:
        conf = util.sanitize_vrrp_config(conf)
        hello_address: List[str] = util.get_hello_sources(conf)
        for address in hello_address:
            util.is_local_address(address)
        if util.is_rfc_compat_configured(conf) and util.running_on_vmware():
            print("RFC compatibility is not supported on VMware\n")
        return

    def rfc_intf_map(self, rpc_input: Dict[str, str]) -> Dict[str, str]:
        xmit_intf: str = rpc_input["vyatta-vrrp-v1:transmit"]
        return self.pc.get_rfc_mapping(xmit_intf)


class State(vci.State):

    def __init__(self, config_impl):
        super().__init__()
        self._conf_obj = config_impl
        if not isinstance(self._conf_obj, AbstractVrrpConfig.ConfigFile):
            raise TypeError("Implementation of config object does not " +
                            "inherit from abstract class, developer needs " +
                            "to fix this ")
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        self.log = logging.getLogger("vyatta-vrrp-vci")
        self.pc = process_control.ProcessControl()

    def get(self) -> Dict[str, Any]:
        if not self.pc.is_running():
            return {}
        file_config: str = self._conf_obj.read_config()
        yang_repr: Dict[str, Any] = self._conf_obj.convert_to_vci_format_dict(
            file_config)
        sysbus = pydbus.SystemBus()
        for intf_type in yang_repr[util.INTERFACE_YANG_NAME]:
            intf_list: List = yang_repr[util.INTERFACE_YANG_NAME][intf_type]
            for intf in intf_list:
                transmit_intf: str = intf["tagnode"]
                if util.VRRP_YANG_NAME not in intf:
                    continue
                if "start-delay" in intf[util.VRRP_YANG_NAME]:
                    del intf[util.VRRP_YANG_NAME]["start-delay"]
                vrrp_instances: List[Dict] = intf[util.VRRP_YANG_NAME]["vrrp-group"]
                state_instances = []
                for vrrp_instance in vrrp_instances:
                    vrid: str = vrrp_instance["tagnode"]
                    instance_name: str = f"vyatta-{transmit_intf}-{vrid}"
                    vrrp_conn: vrrp_dbus.VrrpConnection
                    if instance_name not in \
                            self._conf_obj.vrrp_connections:
                        af_type: str = util.what_ip_version(
                            vrrp_instance["virtual-address"][0].split("/")[0])
                        vrrp_conn = \
                            vrrp_dbus.VrrpConnection(
                                transmit_intf, vrid, af_type, sysbus
                            )
                    else:
                        vrrp_conn = \
                            self._conf_obj.vrrp_connections[instance_name]
                    state_future = vrrp_conn.get_instance_state()
                    state_instances.append(state_future)
                intf[util.VRRP_YANG_NAME]["vrrp-group"] = state_instances
        return yang_repr
