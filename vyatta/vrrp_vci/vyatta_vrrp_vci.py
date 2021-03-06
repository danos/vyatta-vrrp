# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import json
import logging
import subprocess
from typing import Any, Dict, List

import pydbus

import vci  # pylint: disable=import-error


import vyatta.vrrp_vci.keepalived.util as util
from vyatta.vrrp_vci.abstract_vrrp_classes import ConfigFile
from vyatta.vrrp_vci.keepalived.dbus.process_control import ProcessControl
from vyatta.vrrp_vci.keepalived.dbus.vrrp_group_connection import (
    VrrpConnection
)


def send_garp(rpc_input: Dict[str, str]) -> None:
    intf: str = rpc_input[util.RPC_GARP_INTERFACE]
    group: str = str(rpc_input[util.RPC_GARP_GROUP])
    pc = ProcessControl()
    if not pc.is_running():
        return
    try:
        vrrp_conn = VrrpConnection(
            intf, group, 4, pydbus.SystemBus()
        )
        vrrp_conn.garp()
    except Exception as e:
        # Horrible but pydbus doesn't actually export any Exceptions
        log = logging.getLogger(util.LOGGING_MODULE_NAME)
        log.info(
            f"Error trying to send GARP for VRRP group "
            f"{group} on {intf}, does the group/intf combination exist?"
        )
        log.debug(f"Error from the DBus call was: {e}")
    return


def rfc_intf_map(rpc_input: Dict[str, str]) -> Dict[str, str]:
    pc = ProcessControl()
    return pc.get_rfc_mapping(rpc_input[util.RPC_RFC_INTERFACE])


class Config(vci.Config):

    # Class attributes that will be the same across all instances
    def __init__(self, config_impl) -> None:
        super().__init__()
        self._conf_obj = config_impl
        if not isinstance(self._conf_obj, ConfigFile):
            raise TypeError("Implementation of config object does not "
                            "inherit from abstract class, developer needs "
                            "to fix this ")
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        self.log = logging.getLogger(util.LOGGING_MODULE_NAME)
        self.pc = ProcessControl()

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
            f"Got following config from VCI infra: "
            f"{json.dumps(conf, indent=4, sort_keys=True)}"
        )

        self._conf_obj.update(conf)
        self._conf_obj.write_config()
        if self.pc.is_running():
            self.pc.reload_process_config()
        else:
            subprocess.Popen([util.DBUS_NOTIFY_SCRIPT]).pid
            self.pc.start_process()
        self.log.info(
            f"{self._conf_obj.impl_name()} config written to "
            f"{self._conf_obj.config_file_path()}"
        )
        return

    def get(self) -> Dict[str, Any]:
        file_config: str = self._conf_obj.read_config()
        yang_repr: Dict[str, Any] = \
            self._conf_obj.convert_to_vci_format(file_config)
        self.log.info(
            f"{yang_repr} yang repr returned to vci infra"
        )
        return yang_repr

    def check(self, conf: Dict[str, Any]) -> None:
        if conf == {}:
            return
        conf = util.sanitize_vrrp_config(conf)
        hello_address: List[List[str]] = util.get_hello_sources(conf)
        for address in hello_address:
            configured_locally: bool
            try:
                configured_locally = util.is_local_address(address[0])
            except ValueError:
                vci_error = vci.Exception(
                    util.VRRP_NAMESPACE,
                    f"Misconfigured Hello-source-address [{address[0]}] "
                    f"must be IPv4 or IPv6 address",
                    f"/{address[1].replace(' ', '/')}"
                )
                raise vci_error
            if not configured_locally:
                vci_error = vci.Exception(
                    util.VRRP_NAMESPACE,
                    f"Hello-source-address [{address[0]}] must be configured"
                    f" on the interface",
                    f"/{address[1].replace(' ', '/')}"
                )
                raise vci_error
        rfc_compat: bool = util.is_rfc_compat_configured(conf)
        if rfc_compat and util.running_on_vmware():
            self.log.warning("RFC compatibility is not supported on VMWare")
        return


class State(vci.State):

    def __init__(self, config_impl) -> None:
        super().__init__()
        self._conf_obj = config_impl
        if not isinstance(self._conf_obj, ConfigFile):
            raise TypeError("Implementation of config object does not "
                            "inherit from abstract class, developer needs "
                            "to fix this ")
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        self.log = logging.getLogger(util.LOGGING_MODULE_NAME)
        self.pc = ProcessControl()

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
                intf_name_key: str = util.get_namespace(
                    intf, util.YANG_INTERFACE_NAMESPACE
                )
                if intf_name_key == "":
                    continue
                transmit_intf: str = intf[intf_name_key]
                self._generate_interfaces_vrrp_connection_list(
                    intf, transmit_intf, sysbus)
                if util.VIF_YANG_NAME in intf:
                    for vif_intf in intf[util.VIF_YANG_NAME]:
                        vif_transmit_intf: str = \
                            f"{transmit_intf}.{vif_intf[util.YANG_TAGNODE]}"
                        self._generate_interfaces_vrrp_connection_list(
                            vif_intf, vif_transmit_intf, sysbus)
        return yang_repr

    def _generate_interfaces_vrrp_connection_list(
        self, intf: Dict, transmit_intf: str, sysbus
    ) -> None:
        current_vrrp_namespace: str = util.get_namespace(
            intf, util.VRRP_YANG_NAMESPACES
        )
        if current_vrrp_namespace == "":
            return
        if util.YANG_START_DELAY in intf[current_vrrp_namespace]:
            del intf[current_vrrp_namespace][util.YANG_START_DELAY]
        vrrp_instances: List[Dict] = \
            intf[current_vrrp_namespace][util.YANG_VRRP_GROUP]
        state_instances = []
        for vrrp_instance in vrrp_instances:
            vrrp_conn: VrrpConnection
            vrrp_conn = self._generate_vrrp_connection(
                vrrp_instance, transmit_intf, sysbus
            )
            try:
                state_future = vrrp_conn.get_instance_state()
            except KeyError:
                state_future = {
                    util.YANG_INSTANCE_STATE:
                        {
                            util.YANG_IPAO: False,
                            util.YANG_LAST_TRANSITION: 0,
                            util.YANG_RFC_INTF: "",
                            util.YANG_STATE: "FAULT",
                            util.YANG_SYNC_GROUP: ""
                        },
                    util.YANG_TAGNODE: f"{vrrp_instance['tagnode']}"
                }
            state_instances.append(state_future)
        intf[current_vrrp_namespace][util.YANG_VRRP_GROUP] = \
            state_instances

    def _generate_vrrp_connection(
        self, vrrp_instance, transmit_intf, sysbus
    ) -> VrrpConnection:
        vrid: str = vrrp_instance[util.YANG_TAGNODE]
        instance_name: str = f"vyatta-{transmit_intf}-{vrid}"
        vrrp_conn: VrrpConnection = None
        if instance_name not in \
                self._conf_obj.vrrp_connections:
            af_type: int = util.get_ip_version(
                vrrp_instance[util.YANG_VIP][0].split("/")[0])
            vrrp_conn = \
                VrrpConnection(
                    transmit_intf, vrid, af_type, sysbus
                )
        else:
            vrrp_conn = \
                self._conf_obj.vrrp_connections[instance_name]
        return vrrp_conn
