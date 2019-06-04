#! /usr/bin/python3

# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import json
import logging
import pydbus
from typing import Dict
import vci  # pylint: disable=import-error
import vyatta.keepalived.config_file as impl_conf
import vyatta.abstract_vrrp_classes as AbstractVrrpConfig
import vyatta.keepalived.util as util
import vyatta.keepalived.dbus.process_control as process_control
import vyatta.keepalived.dbus.vrrp_group_connection as \
    vrrp_group_connection


def send_garp(rpc_input: Dict[str, str]):
    intf = rpc_input["vyatta-vrrp-v1:interface"]  # type: str
    group = str(rpc_input["vyatta-vrrp-v1:group"])  # type: str
    vrrp_group_connection.garp(intf, group, pydbus.SystemBus())
    return {}


def rfc_intf_map(rpc_input: Dict[str, str]):
    xmit_intf = rpc_input["vyatta-vrrp-v1:transmit"]  # type: str
    return vrrp_group_connection.get_rfc_mapping(
        xmit_intf, pydbus.SystemBus())


class Config(vci.Config):

    # Class attributes that will be the same across all instances
    _conf_obj = impl_conf.\
            KeepalivedConfig()
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    log = logging.getLogger("vyatta-vrrp-vci")

    def _check_conf_object_implementation(self):
        if not isinstance(self._conf_obj, AbstractVrrpConfig.ConfigFile):
            raise TypeError("Implementation of config object does not "
                            "inherit from abstract class, developer needs "
                            "to fix this ")

    def set(self, conf):
        pc = process_control.ProcessControl()
        conf = util.sanitize_vrrp_config(conf)

        # If all the default config has been removed and
        # there's nothing left in the interfaces dictionary
        # just return as we have nothing left to do
        if {} == conf[util.INTERFACE_YANG_NAME]:
            if pc.is_running():
                pc.shutdown_process()
            return
        self.log.debug(
            "Got following config from VCI infra:%s",
            json.dumps(conf, indent=4, sort_keys=True))

        self._check_conf_object_implementation()
        self._conf_obj.update(conf)
        self._conf_obj.write_config()
        if pc.is_running():
            pc.reload_process_config()
        else:
            pc.start_process()
        self.log.info(
            " %s config written to %s",
            self._conf_obj.impl_name(),
            self._conf_obj.config_file_path()
        )
        return

    def get(self):
        self._check_conf_object_implementation()
        file_config = self._conf_obj.read_config()
        yang_repr = self._conf_obj.convert_to_vci_format(file_config)
        self.log.info(
            " %s yang repr returned to vci infra",
            yang_repr
        )
        return yang_repr

    def check(self, conf):
        self._check_conf_object_implementation()
        conf = util.sanitize_vrrp_config(conf)
        hello_address = util.get_hello_sources(conf)
        for address in hello_address:
            util.is_local_address(address)
        if util.is_rfc_compat_configured(conf) and util.running_on_vmware():
            print("RFC compatibility is not supported on VMware\n")
        return


class State(vci.State):
    _conf_obj = impl_conf.\
            KeepalivedConfig()
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    log = logging.getLogger("vyatta-vrrp-vci")

    def _check_conf_object_implementation(self):
        if not isinstance(self._conf_obj, AbstractVrrpConfig.ConfigFile):
            raise TypeError("Implementation of config object does not " +
                            "inherit from abstract class, developer needs " +
                            "to fix this ")

    def get(self):
        self._check_conf_object_implementation()
        file_config = self._conf_obj.read_config()
        yang_repr = self._conf_obj.convert_to_vci_format_dict(file_config)
        sysbus = pydbus.SystemBus()
        for intf_type in yang_repr[util.INTERFACE_YANG_NAME]:
            intf_list = yang_repr[util.INTERFACE_YANG_NAME][intf_type]
            for intf in intf_list:
                transmit_intf = intf["tagnode"]
                del intf[util.VRRP_YANG_NAME]["start-delay"]
                vrrp_instances = intf[util.VRRP_YANG_NAME]["vrrp-group"]
                state_instances = []
                for vrrp_instance in vrrp_instances:
                    vrid = vrrp_instance["tagnode"]
                    af_type = util.what_ip_version(
                        vrrp_instance["virtual-address"][0].split("/")[0])
                    state_future = vrrp_group_connection.get_instance_state(
                        transmit_intf, vrid, af_type, sysbus
                    )
                    state_instances.append(state_future)
                intf[util.VRRP_YANG_NAME]["vrrp-group"] = state_instances
        return yang_repr
