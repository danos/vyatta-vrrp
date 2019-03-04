#! /usr/bin/python3

# Copyright (c) 2019,2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

from unittest import TestCase
import copy
import sys

class FakeVci(object):

    class Config(object):
        def set(self, conf):
            pass
    class State(object):
        def get(object):
            pass

sys.modules['vci'] = FakeVci
from vyatta.vyatta_vrrp_vci import Config

class TestVyattaVrrpVci(TestCase):

    def setup_method(self, method):
        self.test_conf = Config()
        self.INTERFACE_YANG_NAME = "vyatta-interfaces-v1:interfaces"
        self.DATAPLANE_YANG_NAME = "vyatta-interfaces-dataplane-v1:dataplane"
        self.BONDING_YANG_NAME = "vyatta-bonding-v1:bonding"

        self.simple_conf = \
        {self.INTERFACE_YANG_NAME: {
                self.DATAPLANE_YANG_NAME: [
                    {
                        "tagnode": "dp0p1s1",
                        "vyatta-vrrp-v1:vrrp": {
                            "start-delay": 0,
                            "vrrp-group": [
                                {
                                    "accept": False,
                                    "preempt": True,
                                    "priority": 200,
                                    "tagnode": 1,
                                    "version": 2,
                                    "virtual-address": [
                                        "10.10.10.100"
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }
        self.second_intf =\
        {
            "tagnode": "dp0p2",
            "vyatta-vrrp-v1:vrrp": {
                "start-delay": 0,
            }
        }
        self.bonding_list =\
                [
                    {
                        "tagnode": "dp0bond0",
                        "vyatta-vrrp-v1:vrrp": {
                            "start-delay": 0,
                            "vrrp-group": [
                                {
                                    "accept": False,
                                    "preempt": True,
                                    "priority": 200,
                                    "tagnode": 1,
                                    "version": 2,
                                    "virtual-address": [
                                        "10.10.10.100"
                                    ]
                                }
                            ]
                        }
                    }

                ]
        self.vif_dataplane_list =\
                [
                    {
                        "tagnode": "10",
                        "vyatta-vrrp-v1:vrrp": {
                            "start-delay": 0
                        }
                    }
                ]
        self.vif_dataplane_vrrp_group = {\
                                "start-delay": 0,
                                "vrrp-group": [
                                    {
                                        "accept": False,
                                        "preempt": True,
                                        "priority": 200,
                                        "tagnode": 1,
                                        "version": 2,
                                        "virtual-address": [
                                            "10.10.10.100"
                                        ]
                                    }
                                ]
                        }
        self.vif_dataplane_list_sanitized =\
                [
                    {
                        "tagnode": "dp0p1s1.10",
                        "vyatta-vrrp-v1:vrrp": {
                            "start-delay": 0,
                            "vrrp-group": [
                                {
                                    "accept": False,
                                    "preempt": True,
                                    "priority": 200,
                                    "tagnode": 1,
                                    "version": 2,
                                    "virtual-address": [
                                        "10.10.10.100"
                                    ]
                                }
                            ]
                        }
                    }

                ]
        self.vif_bonding_list =\
                [
                    {
                        "tagnode": "100",
                        "vyatta-vrrp-v1:vrrp": {
                            "start-delay": 0
                        }
                    }
                ]
        self.vif_bonding_vrrp_group = {\
                                "start-delay": 0,
                                "vrrp-group": [
                                    {
                                        "accept": False,
                                        "preempt": True,
                                        "priority": 200,
                                        "tagnode": 50,
                                        "version": 2,
                                        "virtual-address": [
                                            "10.10.10.100"
                                        ]
                                    }
                                ]
                        }
        self.vif_bonding_list_sanitized =\
                [
                    {
                        "tagnode": "dp0bond0.100",
                        "vyatta-vrrp-v1:vrrp": {
                            "start-delay": 0,
                            "vrrp-group": [
                                {
                                    "accept": False,
                                    "preempt": True,
                                    "priority": 200,
                                    "tagnode": 50,
                                    "version": 2,
                                    "virtual-address": [
                                        "10.10.10.100"
                                    ]
                                }
                            ]
                        }
                    }

                ]
        self.vif_two_type_list_sanitized = [self.vif_dataplane_list[0], self.vif_bonding_list[0]]


    def test_sanitize_vrrp_config_one_configured(self):
        result = self.test_conf._sanitize_vrrp_config(self.simple_conf)
        expected =\
                {"vyatta-interfaces-v1:interfaces": {
                    "vyatta-interfaces-dataplane-v1:dataplane": [
                    {
                        "tagnode": "dp0p1s1",
                        "vyatta-vrrp-v1:vrrp": {
                            "start-delay": 0,
                            "vrrp-group": [
                                {
                                    "accept": False,
                                    "preempt": True,
                                    "priority": 200,
                                    "tagnode": 1,
                                    "version": 2,
                                    "virtual-address": [
                                        "10.10.10.100"
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }
        assert result == expected

    def test_sanitize_vrrp_config_one_not_configured(self):
        expected =\
        {"vyatta-interfaces-v1:interfaces": {} }
        test_conf =\
        {self.INTERFACE_YANG_NAME: {
                self.DATAPLANE_YANG_NAME: [
                    {
                        "tagnode": "dp0p1s1",
                        "vyatta-vrrp-v1:vrrp": {
                            "start-delay": 0
                        }
                    }
                ]
            }
        }
        assert test_conf != expected
        result = self.test_conf._sanitize_vrrp_config(test_conf)
        assert result == expected

    def test_sanitize_vrrp_config_one_configured_one_not_configured(self):
        expected =\
        {"vyatta-interfaces-v1:interfaces": {
                "vyatta-interfaces-dataplane-v1:dataplane": [
                    {
                        "tagnode": "dp0p1s1",
                        "vyatta-vrrp-v1:vrrp": {
                            "start-delay": 0,
                            "vrrp-group": [
                                {
                                    "accept": False,
                                    "preempt": True,
                                    "priority": 200,
                                    "tagnode": 1,
                                    "version": 2,
                                    "virtual-address": [
                                        "10.10.10.100"
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }
        test_conf = self.simple_conf
        test_conf[self.INTERFACE_YANG_NAME][self.DATAPLANE_YANG_NAME].append(self.second_intf)
        assert test_conf != expected
        result = self.test_conf._sanitize_vrrp_config(test_conf)
        assert result == expected

    def test_sanitize_vrrp_config_two_intf_type(self):
        expected = copy.deepcopy(self.simple_conf)
        expected["vyatta-interfaces-v1:interfaces"]["vyatta-bonding-v1:bonding"] = self.bonding_list
        test_conf = copy.deepcopy(self.simple_conf)
        test_conf[self.INTERFACE_YANG_NAME][self.DATAPLANE_YANG_NAME].append(self.second_intf)
        test_conf[self.INTERFACE_YANG_NAME][self.BONDING_YANG_NAME] = self.bonding_list
        assert test_conf != expected
        result = self.test_conf._sanitize_vrrp_config(test_conf)
        assert result == expected

    def test_sanitize_vrrp_config_remove_empty_vif(self):
        expected = copy.deepcopy(self.simple_conf)
        test_conf = copy.deepcopy(self.simple_conf)
        test_conf[self.INTERFACE_YANG_NAME][self.DATAPLANE_YANG_NAME][0]["vif"] = self.vif_dataplane_list
        result = self.test_conf._sanitize_vrrp_config(test_conf)
        assert expected == result

    def test_sanitize_vrrp_config_move_dataplane_vif(self):
        expected = copy.deepcopy(self.simple_conf)
        expected["vyatta-interfaces-v1:interfaces"]["vif"] = self.vif_dataplane_list_sanitized
        test_conf = copy.deepcopy(self.simple_conf)
        test_conf[self.INTERFACE_YANG_NAME][self.DATAPLANE_YANG_NAME][0]["vif"] = self.vif_dataplane_list
        test_conf[self.INTERFACE_YANG_NAME][self.DATAPLANE_YANG_NAME][0]["vif"][0]["vyatta-vrrp-v1:vrrp"] = self.vif_dataplane_vrrp_group
        result = self.test_conf._sanitize_vrrp_config(test_conf)
        assert expected == result

    def test_sanitize_vrrp_config_move_bonding_vif(self):
        expected = copy.deepcopy(self.simple_conf)
        expected["vyatta-interfaces-v1:interfaces"]["vyatta-bonding-v1:bonding"] = self.bonding_list
        expected["vyatta-interfaces-v1:interfaces"]["vif"] = self.vif_bonding_list_sanitized
        test_conf = copy.deepcopy(self.simple_conf)
        test_conf[self.INTERFACE_YANG_NAME][self.BONDING_YANG_NAME] = self.bonding_list
        test_conf[self.INTERFACE_YANG_NAME][self.BONDING_YANG_NAME][0]["vif"] = self.vif_bonding_list
        test_conf[self.INTERFACE_YANG_NAME][self.BONDING_YANG_NAME][0]["vif"][0]["vyatta-vrrp-v1:vrrp"] = self.vif_bonding_vrrp_group
        result = self.test_conf._sanitize_vrrp_config(test_conf)
        assert expected == result

    def test_sanitize_vrrp_config_move_two_intf_types_vif(self):
        expected = copy.deepcopy(self.simple_conf)
        expected["vyatta-interfaces-v1:interfaces"]["vyatta-bonding-v1:bonding"] = self.bonding_list
        expected["vyatta-interfaces-v1:interfaces"]["vif"] = self.vif_two_type_list_sanitized
        test_conf = copy.deepcopy(self.simple_conf)
        test_conf[self.INTERFACE_YANG_NAME][self.DATAPLANE_YANG_NAME][0]["vif"] = self.vif_dataplane_list
        test_conf[self.INTERFACE_YANG_NAME][self.DATAPLANE_YANG_NAME][0]["vif"][0]["vyatta-vrrp-v1:vrrp"] = self.vif_dataplane_vrrp_group
        test_conf[self.INTERFACE_YANG_NAME][self.BONDING_YANG_NAME] = self.bonding_list
        test_conf[self.INTERFACE_YANG_NAME][self.BONDING_YANG_NAME][0]["vif"] = self.vif_bonding_list
        test_conf[self.INTERFACE_YANG_NAME][self.BONDING_YANG_NAME][0]["vif"][0]["vyatta-vrrp-v1:vrrp"] = self.vif_bonding_vrrp_group
        result = self.test_conf._sanitize_vrrp_config(test_conf)
        assert expected == result



