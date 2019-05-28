#!/usr/bin/env python3

# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only.

import sys
import copy
import pytest

# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=redefined-outer-name


@pytest.fixture
def pydbus_fakes():
    class FakeGi:

        class Gio:
            BusNameOwnerFlags = ""
            BusNameWatcherFlags = ""
            DBusSignalFlags = ""
            BusType = "System"

            class DBusConnection:
                pass

        class GLib:
            class Variant:
                pass

        class GObject:
            pass

        class ExitableWithAliases:

            def __init__(self):
                pass

        class NameOwner():
            pass

    sys.modules['gi.repository'] = FakeGi
    sys.modules['gi.repository.GLib'] = FakeGi.GLib


@pytest.fixture
def test_config(pydbus_fakes):
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
def test_state():
    class FakeVci:

        class Config:
            def set(self, conf):
                pass

        class State:
            def get(self):
                pass

    sys.modules['vci'] = FakeVci
    from vyatta.vyatta_vrrp_vci import State
    return State()


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
        contents = autogeneration_string
        contents += dataplane_group_keepalived_config
        file_handle.write(contents)
    return KeepalivedConfig(file_path)


@pytest.fixture
def tmp_file_syncgroup_keepalived_config(
        tmp_path, syncgroup_keepalived_config):
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
        contents = syncgroup_keepalived_config
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
    file_path = f"{str(tmp_path)}/keepalived.conf"
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
    new_group = copy.deepcopy(generic_group)
    return VrrpGroup("dp0p1s1", "0", new_group)


@pytest.fixture
def fuller_vrrp_group_object(max_config_group):
    from vyatta.keepalived.vrrp import VrrpGroup
    new_group = copy.deepcopy(max_config_group)
    return VrrpGroup("dp0p1s1", "0", new_group, 1)


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
                "10.10.1.100/25"
            ]
        }


@pytest.fixture
def generic_group_state():
    return \
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "",
                "state": "MASTER",
                "sync-group": "",
            }


@pytest.fixture
def instance_state():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "",
                "state": "MASTER",
                "sync-group": "",
            },
            "tagnode": "1"
        }


@pytest.fixture
def instance_state_rfc():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "dp0vrrp1",
                "state": "MASTER",
                "sync-group": "",
            },
            "tagnode": "1"
        }


@pytest.fixture
def generic_v3_group():
    return \
        {
            "accept": False,
            "fast-advertise-interval": 2000,
            "preempt": True,
            "tagnode": 1,
            "version": 3,
            "virtual-address": [
                "10.10.1.100/25"
            ]
        }


@pytest.fixture
def generic_ipv6_group():
    return \
        {
            "accept": False,
            "fast-advertise-interval": 2000,
            "preempt": True,
            "tagnode": 1,
            "version": 3,
            "virtual-address": [
                "2001::2/64",
                "fe80::1/64"
            ]
        }


@pytest.fixture
def accept_v3_group():
    return \
        {
            "accept": True,
            "fast-advertise-interval": 2000,
            "preempt": True,
            "tagnode": 1,
            "version": 3,
            "virtual-address": [
                "10.10.1.100/25"
            ]
        }


@pytest.fixture
def nopreempt_v3_group():
    return \
        {
            "accept": False,
            "fast-advertise-interval": 2000,
            "preempt": False,
            "tagnode": 1,
            "version": 3,
            "virtual-address": [
                "10.10.1.100/25"
            ]
        }


@pytest.fixture
def ah_auth_v3_group():
    return \
        {
            "accept": False,
            "authentication": {
                "password": "help",
                "type": "ah"
            },
            "fast-advertise-interval": 2000,
            "preempt": True,
            "tagnode": 1,
            "version": 3,
            "virtual-address": [
                "10.10.1.100/25"
            ]
        }


@pytest.fixture
def runtransition_v3_group():
    return \
        {
            "accept": False,
            "fast-advertise-interval": 2000,
            "preempt": True,
            "tagnode": 1,
            "version": 3,
            "virtual-address": [
                "10.10.1.100/25"
            ],
            "run-transition-scripts": {
                "master": "master.py",
                "backup": "backup.py",
                "fault": "fault.py"
            }
        }


@pytest.fixture
def legacy_and_enhanced_track_group():
    return \
        {
            "accept": False,
            "fast-advertise-interval": 2000,
            "preempt": True,
            "tagnode": 1,
            "version": 3,
            "virtual-address": [
                "10.10.1.100/25"
            ],
            "track": {
                "interface": [
                    {
                        "name": "dp0p1s1",
                    },
                ]
            },
            "track-interface": [
                {
                    "name": "lo"
                }
            ]
        }


@pytest.fixture
def legacy_and_pathmon_enhanced_track_group(pathmon_yang_name):
    return \
        {
            "accept": False,
            "fast-advertise-interval": 2000,
            "preempt": True,
            "tagnode": 1,
            "version": 3,
            "virtual-address": [
                "10.10.1.100/25"
            ],
            "track": {
                 pathmon_yang_name: {
                     "monitor": [
                         {
                             "name": "test_monitor",
                             "policy": [
                                 {
                                     "name": "test_policy",
                                 }
                             ]
                         }
                     ]
                 }
            },
            "track-interface": [
                {
                    "name": "lo"
                }
            ]
        }


@pytest.fixture
def legacy_track_group():
    return \
        {
            "accept": False,
            "fast-advertise-interval": 2000,
            "preempt": True,
            "tagnode": 1,
            "version": 3,
            "virtual-address": [
                "10.10.1.100/25"
            ],
            "track-interface": [
                {
                    "tagnode": "dp0p1s1",
                    "weight": {
                        "type": "increment",
                        "value": 10
                    }
                },
                {
                    "tagnode": "dp0s2",
                    "weight": {
                        "type": "decrement",
                        "value": 10
                    }
                },
                {
                    "tagnode": "lo"
                }
            ]
        }


@pytest.fixture
def pathmon_track_group(pathmon_yang_name):
    return \
        {
            "accept": False,
            "preempt": True,
            "tagnode": 1,
            "version": 3,
            "virtual-address": [
                "10.10.1.100/25"
            ],
            "track": {
                pathmon_yang_name: {
                    "monitor": [
                        {
                            "name": "test_monitor",
                            "policy": [
                                {
                                    "name": "test_policy",
                                    "weight": {
                                        "type": "increment",
                                        "value": 10
                                    }
                                },
                                {
                                    "name": "tester_policy",
                                    "weight": {
                                        "type": "decrement",
                                        "value": 10
                                    }
                                }
                            ]
                        }
                    ]
                }
            },
        }


@pytest.fixture
def max_config_group(pathmon_yang_name):
    return \
        {
            "accept": False,
            "advertise-interval": 2,
            "authentication": {
                "password": "help",
                "type": "plaintext-password"
            },
            "hello-source-address": "127.0.0.1",
            "notify": {
                "bgp": [
                    None
                ],
                "ipsec": [
                    None
                ]
            },
            "preempt": True,
            "preempt-delay": 10,
            "priority": 200,
            "rfc-compatibility": [
                None
            ],
            "tagnode": 1,
            "track": {
                "interface": [
                    {
                        "name": "dp0p1s1",
                        "weight": {
                            "type": "increment",
                            "value": 10
                        }
                    },
                    {
                        "name": "dp0s2",
                        "weight": {
                            "type": "decrement",
                            "value": 10
                        }
                    },
                    {
                        "name": "lo"
                    }
                ],
                pathmon_yang_name: {
                    "monitor": [
                        {
                            "name": "test_monitor",
                            "policy": [
                                {
                                    "name": "test_policy",
                                    "weight": {
                                        "type": "decrement",
                                        "value": 10
                                    }
                                }
                            ]
                        }
                    ]
                }
            },
            "version": 2,
            "virtual-address": [
                "10.10.1.100/25"
            ]
        }


@pytest.fixture
def disabled_group():
    return \
        {
            "accept": False,
            "disable": [None],
            "preempt": True,
            "priority": 100,
            "tagnode": 1,
            "version": 2,
            "virtual-address": [
                "10.10.1.100/25"
            ]
        }


@pytest.fixture
def preempt_delay_ignored_group():
    return \
        {
            "accept": False,
            "preempt": False,
            "preempt-delay": 10,
            "priority": 200,
            "tagnode": 1,
            "version": 2,
            "virtual-address": [
                "10.10.1.100/25"
            ]
        }


@pytest.fixture
def sync_group1():
    return \
        {
            "accept": False,
            "preempt": True,
            "priority": 200,
            "sync-group": "TEST",
            "tagnode": 1,
            "version": 2,
            "virtual-address": [
                "10.10.1.100"
            ]
        }


@pytest.fixture
def sync_group2():
    return \
        {
            "accept": False,
            "preempt": True,
            "priority": 200,
            "sync-group": "TEST",
            "tagnode": 1,
            "version": 2,
            "virtual-address": [
                "10.10.2.100"
            ]
        }


@pytest.fixture
def syncgroup1_dataplane_interface(sync_group1):
    return \
        {
            "tagnode": "dp0p1s1",
            "vyatta-vrrp-v1:vrrp": {
                "start-delay": 0,
                "vrrp-group": [sync_group1]
            }
        }


@pytest.fixture
def syncgroup2_dataplane_interface(sync_group2):
    return \
        {
            "tagnode": "dp0p1s2",
            "vyatta-vrrp-v1:vrrp": {
                "start-delay": 0,
                "vrrp-group": [sync_group2]
            }
        }


@pytest.fixture
def syncgroup1_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 2
    start_delay 0
    priority 200
    advert_int 1
    virtual_ipaddress {
        10.10.1.100
    }
}"""


@pytest.fixture
def syncgroup2_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s2-1 {
    state BACKUP
    interface dp0p1s2
    virtual_router_id 1
    version 2
    start_delay 0
    priority 200
    advert_int 1
    virtual_ipaddress {
        10.10.2.100
    }
}"""


@pytest.fixture
def syncgroup_keepalived_section():
    return """
vrrp_sync_group TEST {
    group {
        vyatta-dp0p1s1-1
        vyatta-dp0p1s2-1
    }
}
"""


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
def syncgroup_dataplane_list(
        syncgroup1_dataplane_interface,
        syncgroup2_dataplane_interface):
    return [syncgroup1_dataplane_interface, syncgroup2_dataplane_interface]


@pytest.fixture
def dataplane_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 2
    start_delay 0
    priority 200
    advert_int 1
    virtual_ipaddress {
        10.10.1.100/25
    }
}"""


@pytest.fixture
def legacy_track_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 3
    start_delay 0
    priority 100
    advert_int 2
    virtual_ipaddress {
        10.10.1.100/25
    }
    track {
        interface {
            dp0p1s1   weight  +10
            dp0s2   weight  -10
            lo
        }
    }
}"""


@pytest.fixture
def legacy_and_enhanced_track_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 3
    start_delay 0
    priority 100
    advert_int 2
    virtual_ipaddress {
        10.10.1.100/25
    }
    track {
        interface {
            dp0p1s1
            lo
        }
    }
}"""


@pytest.fixture
def legacy_and_pathmon_enhanced_track_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 3
    start_delay 0
    priority 100
    advert_int 2
    virtual_ipaddress {
        10.10.1.100/25
    }
    track {
        interface {
            lo
        }
        pathmon {
            monitor test_monitor    policy test_policy
        }
    }
}"""


@pytest.fixture
def generic_v3_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 3
    start_delay 0
    priority 100
    advert_int 2
    virtual_ipaddress {
        10.10.1.100/25
    }
}"""


@pytest.fixture
def generic_ipv6_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 3
    start_delay 0
    priority 100
    advert_int 2
    virtual_ipaddress {
        fe80::1/64
        2001::2/64
    }
    native_ipv6
}"""


@pytest.fixture
def accept_v3_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 3
    start_delay 0
    priority 100
    advert_int 2
    virtual_ipaddress {
        10.10.1.100/25
    }
    accept
}"""


@pytest.fixture
def runtransition_v3_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 3
    start_delay 0
    priority 100
    advert_int 2
    virtual_ipaddress {
        10.10.1.100/25
    }
    notify_master "master.py master dp0p1s1 1"
    notify_backup "backup.py backup dp0p1s1 1"
    notify_fault "fault.py fault dp0p1s1 1"
}"""


@pytest.fixture
def nopreempt_v3_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 3
    start_delay 0
    priority 100
    advert_int 2
    virtual_ipaddress {
        10.10.1.100/25
    }
    nopreempt
}"""


@pytest.fixture
def ah_auth_v3_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 3
    start_delay 0
    priority 100
    advert_int 2
    virtual_ipaddress {
        10.10.1.100/25
    }
    authentication {
        auth_type AH
        auth_pass help
    }
}"""


@pytest.fixture
def max_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 2
    start_delay 0
    priority 200
    advert_int 2
    virtual_ipaddress {
        10.10.1.100/25
    }
    use_vmac dp0vrrp1
    vmac_xmit_base
    preempt_delay 10
    mcast_src_ip 127.0.0.1
    authentication {
        auth_type PASS
        auth_pass help
    }
    track {
        interface {
            dp0p1s1   weight  +10
            dp0s2   weight  -10
            lo
        }
        pathmon {
            monitor test_monitor    policy test_policy      weight  -10
        }
    }
    notify {
        /opt/vyatta/sbin/vyatta-ipsec-notify.sh
        /opt/vyatta/sbin/notify-bgp
    }
}"""


@pytest.fixture
def pathmon_track_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 3
    start_delay 0
    priority 100
    advert_int 1
    virtual_ipaddress {
        10.10.1.100/25
    }
    track {
        pathmon {
            monitor test_monitor    policy test_policy      weight  +10
            monitor test_monitor    policy tester_policy      weight  -10
        }
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
def switchport_yang_name():
    return "vyatta-switchport-v1:switchport"


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
def pathmon_yang_name():
    return \
        "vyatta-vrrp-path-monitor-track-interfaces-dataplane-v1:path-monitor"


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
def generic_v3_config(top_level_dictionary, interface_yang_name,
                      dataplane_yang_name, dataplane_list,
                      dataplane_interface, generic_v3_group,
                      vrrp_yang_name):
    dataplane_interface[vrrp_yang_name]["vrrp-group"] = \
        [generic_v3_group]
    complex_yang_config = top_level_dictionary
    complex_yang_config[interface_yang_name][dataplane_yang_name] =\
        dataplane_list
    return complex_yang_config


@pytest.fixture
def complex_config(top_level_dictionary, interface_yang_name,
                   dataplane_yang_name, dataplane_list,
                   dataplane_interface, max_config_group,
                   vrrp_yang_name):
    dataplane_interface[vrrp_yang_name]["vrrp-group"] = \
        [max_config_group]
    complex_yang_config = top_level_dictionary
    complex_yang_config[interface_yang_name][dataplane_yang_name] =\
        dataplane_list
    return complex_yang_config


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
def syncgroup_config(top_level_dictionary, interface_yang_name,
                     dataplane_yang_name, syncgroup_dataplane_list):
    syncgroup_yang_config = top_level_dictionary
    syncgroup_yang_config[interface_yang_name][dataplane_yang_name] =\
        syncgroup_dataplane_list
    return syncgroup_yang_config


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
    return f"{autogeneration_string}{dataplane_group_keepalived_config}"


@pytest.fixture
def syncgroup_keepalived_config(autogeneration_string,
                                syncgroup_keepalived_section,
                                syncgroup1_keepalived_config,
                                syncgroup2_keepalived_config):
    return f"{autogeneration_string}" + \
        f"{syncgroup_keepalived_section}" + \
        f"{syncgroup1_keepalived_config}" + \
        f"{syncgroup2_keepalived_config}"


@pytest.fixture
def complete_state_yang(top_level_dictionary, interface_yang_name,
                        dataplane_yang_name, generic_group_state,
                        vrrp_yang_name):
    state_config = top_level_dictionary
    intf = \
        {
            "tagnode": "dp0p1s1",
            vrrp_yang_name:
                {
                    "vrrp-group":
                    [{"instance-state": generic_group_state, "tagnode": "1"}]
                }
        }
    state_config[interface_yang_name][dataplane_yang_name] =\
        [intf]
    return state_config


@pytest.fixture
def mock_show_version_rpc_kvm(monkeypatch):
    import vyatta

    class MockConfigd:

        class Client:

            def __init__(self):
                pass

            def call_rpc_dict(self, source, action, arguments):
                return {"output": "Hypervisor: KVM"}

    monkeypatch.setitem(vyatta.__dict__, "configd", MockConfigd)


@pytest.fixture
def mock_show_version_rpc_vmware(monkeypatch):
    import vyatta

    class MockConfigd:

        class Client:

            def __init__(self):
                pass

            def call_rpc_dict(self, source, action, arguments):
                return {"output": "Hypervisor: VMware"}

    monkeypatch.setitem(vyatta.__dict__, "configd", MockConfigd)


@pytest.fixture
def mock_show_version_rpc_no_hypervisor(monkeypatch):
    import vyatta

    class MockConfigd:

        class Client:

            def __init__(self):
                pass

            def call_rpc_dict(self, source, action, arguments):
                return {"output": ""}

    monkeypatch.setitem(vyatta.__dict__, "configd", MockConfigd)


@pytest.fixture
def mock_pydbus(monkeypatch, pydbus_fakes):
    import pydbus

    class SystemdProxyObject:

        def __init__(self):
            self.vrrp_proxy_obj = VrrpProxyObject()
            self.manager_proxy_obj = ManagerProxyObject()
            self.manager_proxy_obj.add_unit(self.vrrp_proxy_obj)

        def __getitem__(self, name):
            if name == "org.freedesktop.systemd1.Manager":
                return self.manager_proxy_obj
            return self.vrrp_proxy_obj

        def LoadUnit(self, servicefile):  # noqa: N802
            return "/org/freedesktop/systemd1/" + \
                        "unit/vyatta_2dkeepalived_2eservice"

    class PropertyInterface:

        def __init__(self):
            pass

        def GetAll(self, interface_name):  # noqa: N802
            return {'Name': ("vyatta-dp0p1s1-1",),
                    "SyncGroup": ("",),
                    "XmitIntf": ("dp0p1s1",),
                    "State": (2, "Master"),
                    "LastTransition": (0,),
                    "AddressOwner": (False,)
                    }

    class ManagerProxyObject:

        def ___init__(self):
            self.manager_obj = None

        def add_unit(self, obj):
            self.manager_obj = obj

        def RestartUnit(self, service_file, action):  # noqa: N802
            self.manager_obj.SubState = "running"

        def ReloadUnit(self, service_file, action):  # noqa: N802
            self.manager_obj.SubState = "running"

        def StartUnit(self, service_file, action):  # noqa: N802
            self.manager_obj.SubState = "running"

        def StopUnit(self, service_file, action):  # noqa: N802
            self.manager_obj.SubState = "dead"

    class VrrpProxyObject:

        def __init__(self):
            self._state = "dead"

        @property
        def SubState(self):   # noqa: N802
            return self._state

        @SubState.setter
        def SubState(self, new_state):  # noqa: N802
            self._state = new_state

        def __getitem__(self, name):
            return PropertyInterface()

    class MockSystemBus:

        def __init__(self):
            pass

        def get(self, obj_name, obj_path):

            if "/org/freedesktop/systemd1/unit/" + \
                    "vyatta_2dkeepalived_2eservice" == obj_path or \
                    "org.keepalived.Vrrp1" == obj_name:
                vrrp_proxy = VrrpProxyObject()
                return vrrp_proxy
            if "/org/freedesktop/systemd1" == obj_path:
                systemd = SystemdProxyObject()
                return systemd

    monkeypatch.setitem(pydbus.__dict__, "SystemBus", MockSystemBus)


@pytest.fixture
def mock_pydbus_rfc(monkeypatch, pydbus_fakes):
    import pydbus

    class SystemdProxyObject:

        def __init__(self):
            self.vrrp_proxy_obj = VrrpProxyObject()
            self.manager_proxy_obj = ManagerProxyObject()
            self.manager_proxy_obj.add_unit(self.vrrp_proxy_obj)

        def __getitem__(self, name):
            if name == "org.freedesktop.systemd1.Manager":
                return self.manager_proxy_obj
            return self.vrrp_proxy_obj

        def LoadUnit(self, servicefile):  # noqa: N802
            return "/org/freedesktop/systemd1/" + \
                        "unit/vyatta_2dkeepalived_2eservice"

    class PropertyInterface:

        def __init__(self):
            pass

        def GetAll(self, interface_name):  # noqa: N802
            return {'Name': ("vyatta-dp0p1s1-1",),
                    "SyncGroup": ("",),
                    "XmitIntf": ("dp0vrrp1",),
                    "State": (2, "Master"),
                    "LastTransition": (0,),
                    "AddressOwner": (False,)
                    }

    class ManagerProxyObject:

        def ___init__(self):
            self.manager_obj = None

        def add_unit(self, obj):
            self.manager_obj = obj

        def RestartUnit(self, service_file, action):  # noqa: N802
            self.manager_obj.SubState = "running"

        def ReloadUnit(self, service_file, action):  # noqa: N802
            self.manager_obj.SubState = "running"

        def StartUnit(self, service_file, action):  # noqa: N802
            self.manager_obj.SubState = "running"

        def StopUnit(self, service_file, action):  # noqa: N802
            self.manager_obj.SubState = "dead"

    class VrrpProxyObject:

        def __init__(self):
            self._state = "dead"

        @property
        def SubState(self):   # noqa: N802
            return self._state

        @SubState.setter
        def SubState(self, new_state):  # noqa: N802
            self._state = new_state

        def __getitem__(self, name):
            return PropertyInterface()

    class MockSystemBus:

        def __init__(self):
            pass

        def get(self, obj_name, obj_path):

            if "/org/freedesktop/systemd1/unit/" + \
                    "vyatta_2dkeepalived_2eservice" == obj_path or \
                    "org.keepalived.Vrrp1" == obj_name:
                vrrp_proxy = VrrpProxyObject()
                return vrrp_proxy
            if "/org/freedesktop/systemd1" == obj_path:
                systemd = SystemdProxyObject()
                return systemd

    monkeypatch.setitem(pydbus.__dict__, "SystemBus", MockSystemBus)
