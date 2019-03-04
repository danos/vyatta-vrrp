#! /usr/bin/python3

# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import vci
import json
import sys
import vyatta.keepalived.config_file as impl_conf
import vyatta.abstract_vrrp_classes as AbstractVrrpConfig

class Config(vci.Config):

    def __init__(self):
        self._conf_obj = impl_conf.KeepalivedConfig("")
        if not isinstance(self._conf_obj, AbstractVrrpConfig.ConfigFile):
            raise TypeError("Implementation of config object does not inherit from abstract class, developer needs to fix this ")

    def set(self, conf):
        print("Got config for vrrp\n")
        conf = self._sanitize_vrrp_config(conf)

        # If all the default config has been removed and
        # there's nothing left in the interfaces dictionary
        # just return as we have nothing left to do
        if {} == conf["vyatta-interfaces-v1:interfaces"]:
            return
        print(json.dumps(conf, indent=4, sort_keys=True))

        conf_obj = vyatta.keepalived.Keepalived(conf)
        sys.stdout.flush()
        return

    def get(self):
        return {"state": True}

    def check(self, conf):
        return

    def _sanitize_vrrp_config(self, conf):
        intf_dict = conf["vyatta-interfaces-v1:interfaces"]
        new_dict = {}
        for intf_type in intf_dict:
            new_list = []
            count = 0
            for intf in intf_dict[intf_type]:
                if "vrrp-group" in intf["vyatta-vrrp-v1:vrrp"]:
                    new_list.append(intf_dict[intf_type][count])
                count += 1
            if new_list != []:
                new_dict[intf_type] = new_list
        return {"vyatta-interfaces-v1:interfaces": new_dict}




class State(vci.State):
    def get(self):
        return {'state': 'test'}

if __name__ == "__main__":
    (vci.Component("net.vyatta.vci.vrrp")
        .model(vci.Model("net.vyatta.vci.vrrp.v1")
              .config(Config())
              .state(State()))
        .run()
        .wait())
