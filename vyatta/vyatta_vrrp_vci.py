#! /usr/bin/python3

# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import vci
import json
import sys
import logging
import os
import vyatta.keepalived.config_file as impl_conf
import vyatta.abstract_vrrp_classes as AbstractVrrpConfig


class Config(vci.Config):

    def _object_setup(self):
        self._conf_obj = impl_conf.\
                KeepalivedConfig("/etc/keepalived/keepalived_test.conf")
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        self.log = logging.getLogger("vyatta-vrrp-vci")
        if not isinstance(self._conf_obj, AbstractVrrpConfig.ConfigFile):
            raise TypeError("Implementation of config object does not "
                            "inherit from abstract class, developer needs "
                            "to fix this ")

    def set(self, conf):
        self._object_setup()
        conf = self._sanitize_vrrp_config(conf)

        # If all the default config has been removed and
        # there's nothing left in the interfaces dictionary
        # just return as we have nothing left to do
        if {} == conf["vyatta-interfaces-v1:interfaces"]:
            return
        self.log.debug(
            "Got following config from VCI infra:\n{}".format(
                json.dumps(conf, indent=4, sort_keys=True)))

        self._conf_obj.update(conf)
        self._conf_obj.write_config()
        self.log.info(
            " {} config written to {}".format(self._conf_obj.impl_name(),
                                             self._conf_obj.config_file_path()
                                             )
                    )
        return

    def get(self):
        self._object_setup()
        return {"state": True}

    def check(self, conf):
        self._object_setup()
        return

    def _sanitize_vrrp_config(self, conf):
        intf_dict = conf["vyatta-interfaces-v1:interfaces"]
        new_dict = {}
        vif_list = []
        for intf_type in intf_dict:
            new_list = []
            count = 0
            for intf in intf_dict[intf_type]:
                if "vrrp-group" in intf["vyatta-vrrp-v1:vrrp"]:
                    new_list.append(intf_dict[intf_type][count])
                count += 1
                if "vif" in intf:
                    for vif_intf in intf["vif"]:
                        if "vrrp-group" in vif_intf["vyatta-vrrp-v1:vrrp"]:
                            new_vif = vif_intf
                            new_vif["tagnode"] = \
                                "{}.{}".format(intf["tagnode"],
                                               vif_intf["tagnode"])
                            vif_list.append(new_vif)
                    del(intf["vif"])
            if new_list != []:
                new_dict[intf_type] = new_list
        if vif_list != []:
            new_dict["vif"] = vif_list
        return {"vyatta-interfaces-v1:interfaces": new_dict}


class State(vci.State):
    def get(self):
        return {'state': 'test'}


if __name__ == "__main__":
    (vci.Component("net.vyatta.vci.vrrp")
        .model(vci.Model("net.vyatta.vci.vrrp.v1").config(Config())
               .state(State()))
        .run()
        .wait())
