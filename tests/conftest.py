#!/usr/bin/env python3

# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only.

import sys
import pytest

# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=redefined-outer-name


@pytest.fixture
def test_config():
    class FakeVci:

        class Config:
            def set(self, conf):
                pass

        class State:
            def get(self):
                pass

    sys.modules['vci'] = FakeVci
    from vyatta.vyatta_vrrp_vci import Config
    return Config()


@pytest.fixture
def keepalived_config():
    class FakeVci:

        class Config:
            def set(self, conf):
                pass

        class State:
            def get(self):
                pass

    sys.modules['vci'] = FakeVci
    from vyatta.keepalived.config_file import KeepalivedConfig
    return KeepalivedConfig()


@pytest.fixture
def tmp_file_keepalived_config(tmp_path, autogeneration_string,
                               dataplane_group_keepalived_config):
    class FakeVci:

        class Config:
            def set(self, conf):
                pass

        class State:
            def get(self):
                pass

    sys.modules['vci'] = FakeVci
    from vyatta.keepalived.config_file import KeepalivedConfig
    file_path = f"{tmp_path}/keepalived.conf"
    with open(file_path, "w") as file_handle:
        contents = autogeneration_string+"\n"
        contents += dataplane_group_keepalived_config
        file_handle.write(contents)
    return KeepalivedConfig(file_path)


@pytest.fixture
def tmp_file_keepalived_config_no_write(tmp_path):
    class FakeVci:

        class Config:
            def set(self, conf):
                pass

        class State:
            def get(self):
                pass

    sys.modules['vci'] = FakeVci
    from vyatta.keepalived.config_file import KeepalivedConfig
    file_path = f"{tmp_path}/keepalived.conf"
    return KeepalivedConfig(file_path)


@pytest.fixture
def non_default_keepalived_config():
    class FakeVci:

        class Config:
            def set(self, conf):
                pass

        class State:
            def get(self):
                pass

    sys.modules['vci'] = FakeVci
    from vyatta.keepalived.config_file import KeepalivedConfig
    return KeepalivedConfig("/test/file/path.conf")


@pytest.fixture
def simple_vrrp_group_object(generic_group):
    from vyatta.keepalived.vrrp import VrrpGroup
    return VrrpGroup("dp0p1s1", "0", generic_group)


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
def dataplane_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 2
    start_delay 0
    priority 100
    advert_int 1
    virtual_ipaddress {
        10.10.1.100/25
    }
}"""


@pytest.fixture
def second_dataplane_interface():
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
def vrrp_yang_name():
    return "vyatta-vrrp-v1:vrrp"


@pytest.fixture
def top_level_dictionary(interface_yang_name):
    return {interface_yang_name: {}}


@pytest.fixture
def dataplane_interface_dictionary(dataplane_yang_name):
    return {dataplane_yang_name: []}


@pytest.fixture
def bonding_interface_dictionary(bonding_yang_name):
    return {bonding_yang_name: []}


@pytest.fixture
def simple_config(top_level_dictionary, interface_yang_name,
                  dataplane_yang_name, dataplane_list):
    simple_yang_config = top_level_dictionary
    simple_yang_config[interface_yang_name][dataplane_yang_name] =\
        dataplane_list
    return simple_yang_config


@pytest.fixture
def simple_bonding_config(top_level_dictionary, interface_yang_name,
                          bonding_yang_name, bonding_list):
    simple_yang_config = top_level_dictionary
    simple_yang_config[interface_yang_name][bonding_yang_name] = bonding_list
    return simple_yang_config


@pytest.fixture
def simple_dataplane_vif_config(
        top_level_dictionary, interface_yang_name, dataplane_yang_name,
        vif_dataplane_list, dataplane_list):
    simple_yang_config = top_level_dictionary
    simple_yang_config[interface_yang_name][dataplane_yang_name] = \
        dataplane_list
    simple_yang_config[interface_yang_name][dataplane_yang_name][0]["vif"] = \
        vif_dataplane_list
    return simple_yang_config


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
def dataplane_vif_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1.10-2 {
    state BACKUP
    interface dp0p1s1.10
    virtual_router_id 2
    version 2
    start_delay 0
    priority 100
    advert_int 1
    virtual_ipaddress {
        10.10.2.100/25
    }
}"""


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
def bonding_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0bond0-2 {
    state BACKUP
    interface dp0bond0
    virtual_router_id 2
    version 2
    start_delay 60
    priority 100
    advert_int 1
    virtual_ipaddress {
        10.11.2.100/25
    }
}"""


@pytest.fixture
def bonding_list(bonding_interface):
    return [bonding_interface]


@pytest.fixture
def autogeneration_string():
    return """
#
# Autogenerated by /opt/vyatta/sbin/vyatta-vrrp
#


global_defs {
        enable_traps
        enable_dbus
        snmp_socket tcp:localhost:705:1
        enable_snmp_keepalived
        enable_snmp_rfc
}"""


@pytest.fixture
def simple_keepalived_config(autogeneration_string,
                             dataplane_group_keepalived_config):
    return f"{autogeneration_string}\n{dataplane_group_keepalived_config}"
