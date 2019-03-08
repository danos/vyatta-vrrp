#!/usr/bin/env python3

# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only.

import pytest
import sys


class FakeVci:

    class Config:
        def set(self, conf):
            pass

    class State:
        def get(self):
            pass


sys.modules['vci'] = FakeVci
from vyatta.vyatta_vrrp_vci import Config


@pytest.fixture(scope="function")
def test_config():
    return Config()


@pytest.fixture
def generic_group():
    return \
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


@pytest.fixture
def dataplane_interface(generic_group):
    return \
        {
            "tagnode": "dp0p1s1",
            "vyatta-vrrp-v1:vrrp": {
                "start-delay": 0,
                "vrrp-group": [generic_group]
            }
        }


@pytest.fixture
def second_dataplane_interface(generic_group):
    return \
        {
            "tagnode": "dp0p1s2",
            "vyatta-vrrp-v1:vrrp": {
                "start-delay": 0
            }
        }


@pytest.fixture
def dataplane_list(dataplane_interface):
    return [dataplane_interface]


@pytest.fixture
def interface_yang_name():
    return "vyatta-interfaces-v1:interfaces"


@pytest.fixture
def dataplane_yang_name():
    return "vyatta-interfaces-dataplane-v1:dataplane"


@pytest.fixture
def bonding_yang_name():
    return "vyatta-bonding-v1:bonding"


@pytest.fixture
def simple_config(interface_yang_name, dataplane_yang_name,
                  dataplane_list):
    simple_conf = \
        {
            interface_yang_name: {
                dataplane_yang_name: dataplane_list
            }
        }
    return simple_conf


@pytest.fixture
def vif_dataplane_interface():
    return \
        {
            "tagnode": "10",
            "vyatta-vrrp-v1:vrrp": {
                "start-delay": 0
            }
        }


@pytest.fixture
def vif_dataplane_list(vif_dataplane_interface):
    return [vif_dataplane_interface]


@pytest.fixture
def vif_dataplane_interface_sanitized(generic_group):
    return \
        {
            "tagnode": "dp0p1s1.10",
            "vyatta-vrrp-v1:vrrp": {
                "start-delay": 0,
                "vrrp-group": [generic_group]
            }
        }


@pytest.fixture
def vif_dataplane_list_sanitized(vif_dataplane_interface_sanitized):
    return [vif_dataplane_interface_sanitized]


@pytest.fixture
def vif_bonding_interface():
    return \
        {
            "tagnode": "100",
            "vyatta-vrrp-v1:vrrp": {
                "start-delay": 0
            }
        }


@pytest.fixture
def vif_bonding_list(vif_bonding_interface):
    return [vif_bonding_interface]


@pytest.fixture
def vif_bonding_interface_sanitized(generic_group):
    modified_group = generic_group
    modified_group["tagnode"] = 50
    return \
        {
            "tagnode": "dp0bond0.100",
            "vyatta-vrrp-v1:vrrp": {
                "start-delay": 0,
                "vrrp-group": [modified_group]
            }
        }


@pytest.fixture
def vif_bonding_list_sanitized(vif_bonding_interface_sanitized):
    return [vif_bonding_interface_sanitized]


@pytest.fixture
def vif_two_type_list_sanitized(vif_dataplane_list_sanitized,
                                vif_bonding_list_sanitized):
    return [vif_dataplane_list_sanitized[0],
            vif_bonding_list_sanitized[0]]


@pytest.fixture
def bonding_interface(generic_group):
    return \
        {
            "tagnode": "dp0bond0",
            "vyatta-vrrp-v1:vrrp": {
                "start-delay": 0,
                "vrrp-group": [generic_group]
            }
        }


@pytest.fixture
def bonding_list(bonding_interface):
    return [bonding_interface]
