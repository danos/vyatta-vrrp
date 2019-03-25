#! /usr/bin/python3

# Copyright (c) 2019,2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import copy
import json
import pytest


class TestVyattaVrrpVci:

    # pylint: disable=protected-access
    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=too-many-arguments
    def test_sanitize_vrrp_config_one_configured(self, test_config,
                                                 simple_config):
        result = test_config._sanitize_vrrp_config(simple_config)
        expected =\
            {
                "vyatta-interfaces-v1:interfaces": {
                    "vyatta-interfaces-dataplane-v1:dataplane":
                        [
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

    def test_sanitize_vrrp_config_one_not_configured(self, test_config,
                                                     interface_yang_name,
                                                     dataplane_yang_name):
        expected =\
            {interface_yang_name: {}}
        test_conf =\
            {
                interface_yang_name: {
                    dataplane_yang_name: [
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
        result = test_config._sanitize_vrrp_config(test_conf)
        assert result == expected

    def test_sanitize_vrrp_config_one_configured_one_not_configured(
            self, simple_config, test_config, second_dataplane_interface,
            interface_yang_name, dataplane_yang_name):
        expected =\
            {
                "vyatta-interfaces-v1:interfaces": {
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
        test_conf = simple_config
        test_conf[interface_yang_name][dataplane_yang_name]\
            .append(second_dataplane_interface)
        assert test_conf != expected
        result = test_config._sanitize_vrrp_config(test_conf)
        assert result == expected

    def test_sanitize_vrrp_config_two_intf_type(self, simple_config,
                                                bonding_list,
                                                interface_yang_name,
                                                dataplane_yang_name,
                                                bonding_yang_name,
                                                second_dataplane_interface,
                                                test_config):
        expected = copy.deepcopy(simple_config)
        expected[interface_yang_name][bonding_yang_name]\
            = bonding_list
        test_conf = copy.deepcopy(simple_config)
        test_conf[interface_yang_name][dataplane_yang_name]\
            .append(second_dataplane_interface)
        test_conf[interface_yang_name][bonding_yang_name] =\
            bonding_list
        assert test_conf != expected
        result = test_config._sanitize_vrrp_config(test_conf)
        assert result == expected

    def test_sanitize_vrrp_config_remove_empty_vif(self, simple_config,
                                                   test_config,
                                                   interface_yang_name,
                                                   dataplane_yang_name,
                                                   vif_dataplane_list):
        expected = copy.deepcopy(simple_config)
        test_conf = copy.deepcopy(simple_config)
        test_conf[interface_yang_name][dataplane_yang_name][0]["vif"]\
            = vif_dataplane_list
        result = test_config._sanitize_vrrp_config(test_conf)
        assert expected == result

    def test_sanitize_vrrp_config_move_dataplane_vif(
            self, simple_config, test_config, interface_yang_name,
            dataplane_yang_name, generic_group,
            vif_dataplane_list_sanitized,
            vif_dataplane_list):
        expected = copy.deepcopy(simple_config)
        test_conf = copy.deepcopy(simple_config)
        expected[interface_yang_name]["vif"] =\
            vif_dataplane_list_sanitized
        first_intf = test_conf[interface_yang_name][dataplane_yang_name][0]
        first_intf["vif"] = vif_dataplane_list
        first_intf["vif"][0]["vyatta-vrrp-v1:vrrp"]["vrrp-group"]\
            = [generic_group]
        result = test_config._sanitize_vrrp_config(test_conf)
        assert expected == result

    def test_sanitize_vrrp_config_move_bonding_vif(self, simple_config,
                                                   test_config,
                                                   interface_yang_name,
                                                   bonding_yang_name,
                                                   bonding_list,
                                                   generic_group,
                                                   vif_bonding_list,
                                                   vif_bonding_list_sanitized):
        expected = copy.deepcopy(simple_config)
        expected[interface_yang_name][bonding_yang_name]\
            = bonding_list
        expected[interface_yang_name]["vif"] =\
            vif_bonding_list_sanitized
        test_conf = copy.deepcopy(simple_config)
        test_conf[interface_yang_name][bonding_yang_name] =\
            bonding_list
        test_conf[interface_yang_name][bonding_yang_name][0]["vif"] =\
            vif_bonding_list
        first_intf = test_conf[interface_yang_name][bonding_yang_name][0]
        first_intf["vif"][0]["vyatta-vrrp-v1:vrrp"]["vrrp-group"]\
            = [generic_group]
        result = test_config._sanitize_vrrp_config(test_conf)
        assert expected == result

    def test_sanitize_vrrp_config_move_two_intf_types_vif(
            self, simple_config, interface_yang_name, dataplane_yang_name,
            bonding_list, bonding_yang_name, vif_dataplane_list,
            vif_two_type_list_sanitized, generic_group,
            vif_bonding_list, test_config):
        expected = copy.deepcopy(simple_config)
        expected[interface_yang_name][bonding_yang_name]\
            = bonding_list
        expected[interface_yang_name]["vif"] =\
            vif_two_type_list_sanitized
        test_conf = copy.deepcopy(simple_config)
        test_conf[interface_yang_name][dataplane_yang_name][0]["vif"]\
            = vif_dataplane_list
        first_intf = test_conf[interface_yang_name][dataplane_yang_name][0]
        first_intf["vif"][0]["vyatta-vrrp-v1:vrrp"]["vrrp-group"]\
            = [generic_group]
        test_conf[interface_yang_name][bonding_yang_name] =\
            bonding_list
        test_conf[interface_yang_name][bonding_yang_name][0]["vif"] =\
            vif_bonding_list
        second_intf = test_conf[interface_yang_name][bonding_yang_name][0]
        second_intf["vif"][0]["vyatta-vrrp-v1:vrrp"]["vrrp-group"]\
            = [generic_group]
        result = test_config._sanitize_vrrp_config(test_conf)
        assert expected == result

    def test_check_conf_object_impl_incorrect(self, test_config):
        test_config._conf_obj = int(42)
        with pytest.raises(TypeError):
            test_config._check_conf_object_implementation()

    def test_check_conf_object_impl_correct(self, test_config):
        try:
            test_config._check_conf_object_implementation()
        except TypeError:
            pytest.fail("Unexpected TypeError")
