#! /usr/bin/python3

# Copyright (c) 2019,2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

from unittest import TestCase, mock
import logging
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

        self.simple_conf = \
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


    def test_remove_empty_vrrp_one_configured(self):
        result = self.test_conf.remove_empty_vrrp(self.simple_conf)
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

    def test_remove_empty_vrrp_one_not_configured(self):
        expected =\
        {"vyatta-interfaces-v1:interfaces": {} }
        test_conf =\
        {"vyatta-interfaces-v1:interfaces": {
                "vyatta-interfaces-dataplane-v1:dataplane": [
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
        result = self.test_conf.remove_empty_vrrp(test_conf)
        assert result == expected

    def test_remove_empty_vrrp_one_configured_one_not_configured(self):
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
        test_conf["vyatta-interfaces-v1:interfaces"]["vyatta-interfaces-dataplane-v1:dataplane"].append(self.second_intf)
        assert test_conf != expected
        result = self.test_conf.remove_empty_vrrp(test_conf)
        assert result == expected

    def test_remove_empty_vrrp_two_intf_type(self):
        expected = copy.deepcopy(self.simple_conf)
        expected["vyatta-interfaces-v1:interfaces"]["vyatta-bonding-v1:bonding"] = self.bonding_list
        test_conf = copy.deepcopy(self.simple_conf)
        test_conf["vyatta-interfaces-v1:interfaces"]["vyatta-interfaces-dataplane-v1:dataplane"].append(self.second_intf)
        test_conf["vyatta-interfaces-v1:interfaces"]["vyatta-bonding-v1:bonding"] = self.bonding_list
        assert test_conf != expected
        result = self.test_conf.remove_empty_vrrp(test_conf)
        assert result == expected

