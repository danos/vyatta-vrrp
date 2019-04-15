#! /usr/bin/python3

# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import json
import logging
import vci  # pylint: disable=import-error
import vyatta.keepalived.config_file as impl_conf
import vyatta.abstract_vrrp_classes as AbstractVrrpConfig
import vyatta.keepalived.util as util


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
        conf = util.sanitize_vrrp_config(conf)

        # If all the default config has been removed and
        # there's nothing left in the interfaces dictionary
        # just return as we have nothing left to do
        if {} == conf[util.INTERFACE_YANG_NAME]:
            return
        self.log.debug(
            "Got following config from VCI infra:%s",
            json.dumps(conf, indent=4, sort_keys=True))

        self._check_conf_object_implementation()
        self._conf_obj.update(conf)
        self._conf_obj.write_config()
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
    def get(self):
        return {util.INTERFACE_YANG_NAME:
                {util.DATAPLANE_YANG_NAME: []}}


if __name__ == "__main__":
    (vci.Component("net.vyatta.vci.vrrp")
     .model(vci.Model("net.vyatta.vci.vrrp.v1").config(Config())
            .state(State()))
     .run()
     .wait())
