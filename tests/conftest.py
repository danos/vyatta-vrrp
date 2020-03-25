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
def calendar_fakes():
    class Calendar:

        def timegm(self):
            return 3

    sys.modules['calendar'] = Calendar


@pytest.fixture
def tmp_file_keepalived_config_no_write(tmp_path):
    class FakeVci:

        class Config:
            def set(self, conf):
                pass

        class State:
            def get(self):
                pass

        class Client:
            def emit(self):
                pass

    sys.modules['vci'] = FakeVci
    from vyatta.keepalived.config_file import KeepalivedConfig
    file_path = f"{str(tmp_path)}/keepalived.conf"
    return KeepalivedConfig(file_path)


@pytest.fixture
def test_config(
    pydbus_fakes, monkeypatch, tmp_path,
    tmp_file_keepalived_config_no_write
):

    class FakeVci:

        class Config:
            def __init__(self):
                pass

            def set(self, conf):
                pass

        class State:
            def get(self):
                pass

        class Client:
            def emit(self):
                pass

    sys.modules['vci'] = FakeVci
    import vyatta.keepalived.dbus.process_control as process_ctrl

    class MockProcess(process_ctrl.ProcessControl):

        def __init__(self):
            super().__init__()
            self.systemd_default_file_path = \
                f"{str(tmp_path)}/vyatta-keepalived"
            self.snmpd_conf_file_path = \
                f"{str(tmp_path)}/snmpd.conf"
    monkeypatch.setitem(
        process_ctrl.__dict__,
        "ProcessControl",
        MockProcess)
    from vyatta.vyatta_vrrp_vci import Config
    return Config(tmp_file_keepalived_config_no_write)


@pytest.fixture
def test_state(tmp_file_keepalived_config_no_write):
    class FakeVci:

        class Config:
            def set(self, conf):
                pass

        class State:
            def get(self):
                pass

        class Client:
            def emit(self):
                pass

    sys.modules['vci'] = FakeVci
    from vyatta.vyatta_vrrp_vci import State
    return State(tmp_file_keepalived_config_no_write)


@pytest.fixture
def keepalived_config(pydbus_fakes):
    class FakeVci:

        class Config:
            def set(self, conf):
                pass

        class State:
            def get(self):
                pass

        class Client:
            def emit(self):
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

        class Client:
            def emit(self):
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

        class Client:
            def emit(self):
                pass

    sys.modules['vci'] = FakeVci
    from vyatta.keepalived.config_file import KeepalivedConfig
    file_path = f"{tmp_path}/keepalived.conf"
    with open(file_path, "w") as file_handle:
        contents = syncgroup_keepalived_config
        file_handle.write(contents)
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

        class Client:
            def emit(self):
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


"""Show vrrp fixtures"""


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
def generic_rfc_group():
    return \
        {
            "accept": False,
            "preempt": True,
            "priority": 200,
            "rfc-compatibility": [
                None
            ],
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
def generic_group_show_summary():
    return """
                                 RFC        Addr   Last        Sync
Interface         Group  State   Compliant  Owner  Transition  Group
---------         -----  -----   ---------  -----  ----------  -----
dp0p1s1           1      MASTER  no         no     3s          <none>

"""


@pytest.fixture
def generic_group_rfc_show_summary():
    return """
                                 RFC        Addr   Last        Sync
Interface         Group  State   Compliant  Owner  Transition  Group
---------         -----  -----   ---------  -----  ----------  -----
dp0p1s1           1      MASTER  dp0vrrp1   no     3s          <none>

"""


@pytest.fixture
def generic_group_rfc_sync_show_summary():
    return """
                                 RFC        Addr   Last        Sync
Interface         Group  State   Compliant  Owner  Transition  Group
---------         -----  -----   ---------  -----  ----------  -----
dp0p1s1           1      MASTER  dp0vrrp1   no     3s          TEST

"""


@pytest.fixture
def generic_group_rfc_ipao_show_summary():
    return """
                                 RFC        Addr   Last        Sync
Interface         Group  State   Compliant  Owner  Transition  Group
---------         -----  -----   ---------  -----  ----------  -----
dp0p1s1           1      MASTER  dp0vrrp1   yes    3s          <none>

"""


@pytest.fixture
def generic_group_rfc_switch_show_summary():
    return """
                                 RFC        Addr   Last        Sync
Interface         Group  State   Compliant  Owner  Transition  Group
---------         -----  -----   ---------  -----  ----------  -----
sw0.10            1      MASTER  sw0vrrp1   no     3s          <none>

"""


"""Show vrrp detail fixtures"""


@pytest.fixture
def generic_group_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = MASTER
   Last transition = 3 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s1
   Transmitting device = dp0p1s1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 100
   Effective priority = 100
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0p1s1 scope global
"""


@pytest.fixture
def detailed_simple_keepalived_state():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "",
                "state": "MASTER",
                "sync-group": "",
                "version": 2,
                "src-ip": "10.10.1.1",
                "base-priority": 100,
                "effective-priority": 100,
                "advert-interval": "2 sec",
                "accept": True,
                "preempt": True,
                "auth-type": None,
                "virtual-ips": [
                    "10.10.1.100/32"
                ]
            },
            "tagnode": "1"
        }


@pytest.fixture
def generic_group_show_detail():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        MASTER
  Last transition:              3s

  Version:                      2
  Configured Priority:          100
  Effective Priority:           100
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled

  VIP count:                    1
    10.10.1.100/32

"""


@pytest.fixture
def generic_group_rfc_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Transmitting device = dp0vrrp1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 100
   Effective priority = 100
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0vrrp1 scope global
"""


@pytest.fixture
def generic_group_rfc_show_detail():
    # flake8: noqa: W291
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        MASTER
  Last transition:              3s

  Version:                      2
  RFC Compliant                 
  Virtual MAC interface:        dp0vrrp1
  Address Owner:                no

  Source Address:               10.10.1.1
  Configured Priority:          100
  Effective Priority:           100
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled

  VIP count:                    1
    10.10.1.100/32

"""  # noqa: W291


@pytest.fixture
def detailed_rfc_simple_keepalived_state():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "dp0vrrp1",
                "state": "MASTER",
                "sync-group": "",
                "version": 2,
                "src-ip": "10.10.1.1",
                "base-priority": 100,
                "effective-priority": 100,
                "advert-interval": "2 sec",
                "accept": True,
                "preempt": True,
                "auth-type": None,
                "virtual-ips": [
                    "10.10.1.100/32"
                ]
            },
            "tagnode": "1"
        }


@pytest.fixture
def generic_group_rfc_sync_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Transmitting device = dp0vrrp1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 100
   Effective priority = 100
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0vrrp1 scope global
------< VRRP Sync groups >------
 VRRP Sync Group = TEST, MASTER
   monitor = vyatta-dp0p1s1-1
"""


@pytest.fixture
def generic_group_rfc_sync_show_detail():
    # flake8: noqa: W291
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        MASTER
  Last transition:              3s

  Version:                      2
  RFC Compliant                 
  Virtual MAC interface:        dp0vrrp1
  Address Owner:                no

  Source Address:               10.10.1.1
  Configured Priority:          100
  Effective Priority:           100
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled

  Sync-group:                   TEST

  VIP count:                    1
    10.10.1.100/32

"""  # noqa: W291


@pytest.fixture
def detailed_rfc_sync_simple_keepalived_state():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "dp0vrrp1",
                "state": "MASTER",
                "sync-group": "TEST",
                "version": 2,
                "src-ip": "10.10.1.1",
                "base-priority": 100,
                "effective-priority": 100,
                "advert-interval": "2 sec",
                "accept": True,
                "preempt": True,
                "auth-type": None,
                "virtual-ips": [
                    "10.10.1.100/32"
                ]
            },
            "tagnode": "1"
        }


@pytest.fixture
def generic_group_ipao_rfc_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Transmitting device = dp0vrrp1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 100
   Effective priority = 255
   Address owner = yes
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0vrrp1 scope global
"""


@pytest.fixture
def generic_group_rfc_ipao_show_detail():
    # flake8: noqa: W291
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        MASTER
  Last transition:              3s

  Version:                      2
  RFC Compliant                 
  Virtual MAC interface:        dp0vrrp1
  Address Owner:                yes

  Configured Priority:          100
  Effective Priority:           255
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled

  VIP count:                    1
    10.10.1.100/32

"""  # noqa: W291


@pytest.fixture
def detailed_rfc_ipao_simple_keepalived_state():
    return \
        {
            "instance-state":
            {
                "address-owner": True,
                "last-transition": 0,
                "rfc-interface": "dp0vrrp1",
                "state": "MASTER",
                "sync-group": "",
                "version": 2,
                "src-ip": "10.10.1.1",
                "base-priority": 100,
                "effective-priority": 255,
                "advert-interval": "2 sec",
                "accept": True,
                "preempt": True,
                "auth-type": None,
                "virtual-ips": [
                    "10.10.1.100/32"
                ]
            },
            "tagnode": "1"
        }


@pytest.fixture
def backup_generic_group_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = BACKUP
   Master router = 10.10.1.1
   Master priority = 200
   Last transition = 1568898694 (Thu Sep 19 13:11:34 2019)
   Listening device = dp0p1s1
   Transmitting device = dp0p1s1
   Using src_ip = 10.10.1.2
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 150
   Effective priority = 150
   Address owner = no
   Advert interval = 1 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/24 dev dp0p1s1 scope global
    """


@pytest.fixture
def detailed_backup_generic_group_show_detail():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        BACKUP
  Last transition:              3s

  Master router:                10.10.1.1
  Master priority:              100

  Version:                      2
  Configured Priority:          50
  Effective Priority:           50
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled

  VIP count:                    1
    10.10.1.100/24

"""


@pytest.fixture
def detailed_backup_simple_keepalived_state():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "",
                "state": "BACKUP",
                "sync-group": "",
                "version": 2,
                "master-router": "10.10.1.1",
                "master-priority": 100,
                "src-ip": "10.10.1.1",
                "base-priority": 50,
                "effective-priority": 50,
                "advert-interval": "2 sec",
                "accept": True,
                "preempt": True,
                "auth-type": None,
                "virtual-ips": [
                    "10.10.1.100/24"
                ]
            },
            "tagnode": "1"
        }


@pytest.fixture
def backup_generic_group_track_intf_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = BACKUP
   Master router = 10.10.1.1
   Master priority = 200
   Last transition = 1568898694 (Thu Sep 19 13:11:34 2019)
   Listening device = dp0p1s1
   Transmitting device = dp0p1s1
   Using src_ip = 10.10.1.2
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 150
   Effective priority = 150
   Address owner = no
   Advert interval = 1 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Tracked interfaces = 1
------< NIC >------
 Name = dp0s2
 index = 5
 IPv4 address = 192.168.252.107
 IPv6 address = fe80::4060:2ff:fe00:2
 MAC = 42:60:02:00:00:02
 is UP
 is RUNNING
 weight = 10
 MTU = 1500
 HW Type = ETHERNET
 Enabling NIC ioctl refresh polling
   Virtual IP = 1
     10.10.1.100/24 dev dp0p1s1 scope global
    """


@pytest.fixture
def detailed_backup_generic_group_track_intf_show_detail():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        BACKUP
  Last transition:              3s

  Master router:                10.10.1.1
  Master priority:              100

  Version:                      2
  Configured Priority:          50
  Effective Priority:           50
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled

  Tracked Interfaces count:     1
    dp0s2   state UP      weight -10
  VIP count:                    1
    10.10.1.100/24

"""


@pytest.fixture
def detailed_backup_track_intf_simple_keepalived_state():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "",
                "state": "BACKUP",
                "sync-group": "",
                "version": 2,
                "master-router": "10.10.1.1",
                "master-priority": 100,
                "src-ip": "10.10.1.1",
                "base-priority": 50,
                "effective-priority": 50,
                "advert-interval": "2 sec",
                "accept": True,
                "preempt": True,
                "auth-type": None,
                "track": {
                    "interface": [
                        {
                            "name": "dp0s2", "state": "UP",
                            "weight": "-10"
                        }
                    ]
                },
                "virtual-ips": [
                    "10.10.1.100/24"
                ]
            },
            "tagnode": "1"
        }


@pytest.fixture
def backup_generic_group_track_intf_no_weight_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = BACKUP
   Master router = 10.10.1.1
   Master priority = 200
   Last transition = 1568898694 (Thu Sep 19 13:11:34 2019)
   Listening device = dp0p1s1
   Transmitting device = dp0p1s1
   Using src_ip = 10.10.1.2
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 150
   Effective priority = 150
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Tracked interfaces = 1
------< NIC >------
 Name = dp0s2
 index = 5
 IPv4 address = 192.168.252.107
 IPv6 address = fe80::4060:2ff:fe00:2
 MAC = 42:60:02:00:00:02
 is UP
 is RUNNING
 MTU = 1500
 HW Type = ETHERNET
 Enabling NIC ioctl refresh polling
   Virtual IP = 1
     10.10.1.100/24 dev dp0p1s1 scope global
    """


@pytest.fixture
def detailed_backup_generic_group_track_intf_no_weight_show_detail():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        BACKUP
  Last transition:              3s

  Master router:                10.10.1.1
  Master priority:              100

  Version:                      2
  Configured Priority:          50
  Effective Priority:           50
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled

  Tracked Interfaces count:     1
    dp0s2   state UP      
  VIP count:                    1
    10.10.1.100/24

"""  # noqa: W291


@pytest.fixture
def detailed_backup_track_intf_no_weight_simple_keepalived_state():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "",
                "state": "BACKUP",
                "sync-group": "",
                "version": 2,
                "master-router": "10.10.1.1",
                "master-priority": 100,
                "src-ip": "10.10.1.1",
                "base-priority": 50,
                "effective-priority": 50,
                "advert-interval": "2 sec",
                "accept": True,
                "preempt": True,
                "auth-type": None,
                "track": {
                    "interface": [
                        {
                            "name": "dp0s2", "state": "UP"
                        }
                    ]
                },
                "virtual-ips": [
                    "10.10.1.100/24"
                ]
            },
            "tagnode": "1"
        }


@pytest.fixture
def backup_generic_group_track_pathmon_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = BACKUP
   Master router = 10.10.1.1
   Master priority = 200
   Last transition = 1568898694 (Thu Sep 19 13:11:34 2019)
   Listening device = dp0p1s1
   Transmitting device = dp0p1s1
   Using src_ip = 10.10.1.2
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 150
   Effective priority = 150
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Tracked path-monitors = 1
   Monitor = test_monitor
   Policy = test_policy
   Weight = 10
   Status = COMPLIANT
   Virtual IP = 1
     10.10.1.100/24 dev dp0p1s1 scope global
    """


@pytest.fixture
def detailed_backup_generic_group_track_pathmon_show_detail():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        BACKUP
  Last transition:              3s

  Master router:                10.10.1.1
  Master priority:              100

  Version:                      2
  Configured Priority:          50
  Effective Priority:           50
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled

  Tracked Path Monitor count:   1
    test_monitor
      test_policy  COMPLIANT  weight 10
  VIP count:                    1
    10.10.1.100/24

"""  # noqa: W291


@pytest.fixture
def detailed_backup_track_pathmon_simple_keepalived_state():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "",
                "state": "BACKUP",
                "sync-group": "",
                "version": 2,
                "master-router": "10.10.1.1",
                "master-priority": 100,
                "src-ip": "10.10.1.1",
                "base-priority": 50,
                "effective-priority": 50,
                "advert-interval": "2 sec",
                "accept": True,
                "preempt": True,
                "auth-type": None,
                "track": {
                    "monitor": [
                        {
                            "name": "test_monitor",
                            "policies": [
                                {
                                    "name": "test_policy",
                                    "state": "COMPLIANT",
                                    "weight": "10"
                                }
                            ]
                        }
                    ]
                },
                "virtual-ips": [
                    "10.10.1.100/24"
                ]
            },
            "tagnode": "1"
        }


@pytest.fixture
def backup_generic_group_track_route_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = BACKUP
   Master router = 10.10.1.1
   Master priority = 200
   Last transition = 1568898694 (Thu Sep 19 13:11:34 2019)
   Listening device = dp0p1s1
   Transmitting device = dp0p1s1
   Using src_ip = 10.10.1.2
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 150
   Effective priority = 150
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Tracked routes = 1
   Network = 10.10.10.0
   Prefix = 24
   Status = DOWN
   Weight = 10
   Virtual IP = 1
     10.10.1.100/24 dev dp0p1s1 scope global
    """


@pytest.fixture
def detailed_backup_generic_group_track_route_show_detail():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        BACKUP
  Last transition:              3s

  Master router:                10.10.1.1
  Master priority:              100

  Version:                      2
  Configured Priority:          50
  Effective Priority:           50
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled

  Tracked routes count:         1
    10.10.10.0/24   state DOWN      weight 10
  VIP count:                    1
    10.10.1.100/24

"""


@pytest.fixture
def detailed_backup_track_route_simple_keepalived_state():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "",
                "state": "BACKUP",
                "sync-group": "",
                "version": 2,
                "master-router": "10.10.1.1",
                "master-priority": 100,
                "src-ip": "10.10.1.1",
                "base-priority": 50,
                "effective-priority": 50,
                "advert-interval": "2 sec",
                "accept": True,
                "preempt": True,
                "auth-type": None,
                "track": {
                    "route": [
                        {
                            "name": "10.10.10.0/24",
                            "state": "DOWN",
                            "weight": "10"
                        }
                    ]
                },
                "virtual-ips": [
                    "10.10.1.100/24"
                ]
            },
            "tagnode": "1"
        }


@pytest.fixture
def generic_v3_group_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 3
   State = MASTER
   Last transition = 3 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s1
   Transmitting device = dp0p1s1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 100
   Effective priority = 100
   Address owner = no
   Advert interval = 2000 milli-sec
   Accept = disabled
   Preempt = enabled
   Promote_secondaries = enabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0p1s1 scope global
"""


@pytest.fixture
def detailed_v3_simple_keepalived_state():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "",
                "state": "MASTER",
                "sync-group": "",
                "version": 3,
                "src-ip": "10.10.1.1",
                "base-priority": 100,
                "effective-priority": 100,
                "advert-interval": "2000 milli-sec",
                "accept": True,
                "preempt": True,
                "auth-type": None,
                "virtual-ips": [
                    "10.10.1.100/32"
                ]
            },
            "tagnode": "1"
        }


@pytest.fixture
def generic_v3_group_show_detail():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        MASTER
  Last transition:              3s

  Version:                      3
  Configured Priority:          100
  Effective Priority:           100
  Advertisement interval:       2000 milli-sec
  Preempt:                      enabled
  Accept:                       enabled

  VIP count:                    1
    10.10.1.100/32

"""


@pytest.fixture
def generic_group_start_delay_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = MASTER
   Last transition = 3 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s1
   Transmitting device = dp0p1s1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 100
   Effective priority = 100
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Start delay = 30 secs
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0p1s1 scope global
"""


@pytest.fixture
def detailed_start_delay_simple_keepalived_state():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "",
                "state": "MASTER",
                "sync-group": "",
                "version": 2,
                "src-ip": "10.10.1.1",
                "base-priority": 100,
                "effective-priority": 100,
                "advert-interval": "2 sec",
                "accept": True,
                "preempt": True,
                "start-delay": "30 secs",
                "auth-type": None,
                "virtual-ips": [
                    "10.10.1.100/32"
                ]
            },
            "tagnode": "1"
        }


@pytest.fixture
def generic_start_delay_group_show_detail():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        MASTER
  Last transition:              3s

  Version:                      2
  Configured Priority:          100
  Effective Priority:           100
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled
  Start delay:                  30 secs

  VIP count:                    1
    10.10.1.100/32

"""


@pytest.fixture
def generic_group_preempt_delay_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = MASTER
   Last transition = 3 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s1
   Transmitting device = dp0p1s1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 100
   Effective priority = 100
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Preempt delay = 30 secs
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0p1s1 scope global
"""


@pytest.fixture
def detailed_preempt_delay_simple_keepalived_state():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "",
                "state": "MASTER",
                "sync-group": "",
                "version": 2,
                "src-ip": "10.10.1.1",
                "base-priority": 100,
                "effective-priority": 100,
                "advert-interval": "2 sec",
                "accept": True,
                "preempt": True,
                "preempt-delay": "30 secs",
                "auth-type": None,
                "virtual-ips": [
                    "10.10.1.100/32"
                ]
            },
            "tagnode": "1"
        }


@pytest.fixture
def generic_preempt_delay_group_show_detail():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        MASTER
  Last transition:              3s

  Version:                      2
  Configured Priority:          100
  Effective Priority:           100
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled
  Preempt delay:                30 secs

  VIP count:                    1
    10.10.1.100/32

"""

"""Show vrrp sync group fixtures"""


@pytest.fixture
def sync_group_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s2-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s2
   Transmitting device = dp0p1s2
   Using src_ip = 10.10.2.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 200
   Effective priority = 200
   Address owner = no
   Advert interval = 1 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.2.100/32 dev dp0p1s2 scope global
 VRRP Instance = vyatta-dp0p1s3-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s3
   Transmitting device = dp0p1s3
   Using src_ip = 10.10.3.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Base priority = 200
   Effective priority = 200
   Address owner = no
   Advert interval = 1 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.3.100/32 dev dp0p1s3 scope global
------< VRRP Sync groups >------
 VRRP Sync Group = TEST, MASTER
   monitor = vyatta-dp0p1s2-1
   monitor = vyatta-dp0p1s1-1
"""


@pytest.fixture
def sync_group_simple_keepalived_state():
    return \
        {
            "sync-groups":
            [
                {
                    "name": "TEST",
                    "state": "MASTER",
                    "members": [
                        "vyatta-dp0p1s2-1",
                        "vyatta-dp0p1s1-1"
                    ]
                }
            ]
        }


@pytest.fixture
def detailed_multi_group_first_simple_keepalived_state():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "",
                "state": "MASTER",
                "sync-group": "TEST",
                "version": 2,
                "src-ip": "10.10.1.1",
                "base-priority": 200,
                "effective-priority": 200,
                "advert-interval": "1 sec",
                "accept": True,
                "preempt": True,
                "auth-type": None,
                "virtual-ips": [
                    "10.10.1.100/32"
                ]
            },
            "tagnode": "1"
        }


@pytest.fixture
def detailed_multi_group_second_simple_keepalived_state():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "",
                "state": "MASTER",
                "sync-group": "TEST",
                "version": 2,
                "src-ip": "10.10.2.1",
                "base-priority": 200,
                "effective-priority": 200,
                "advert-interval": "1 sec",
                "accept": True,
                "preempt": True,
                "auth-type": None,
                "virtual-ips": [
                    "10.10.2.100/32"
                ]
            },
            "tagnode": "1"
        }


@pytest.fixture
def generic_sync_group_show_sync():
    return """
--------------------------------------------------
Group: TEST
---------
  State: MASTER
  Monitoring:
    Interface: dp0p1s1, Group: 1
    Interface: dp0p1s2, Group: 1

"""


@pytest.fixture
def multi_group_sync_group_show_detailed():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        MASTER
  Last transition:              3s

  Version:                      2
  Configured Priority:          200
  Effective Priority:           200
  Advertisement interval:       1 sec
  Authentication type:          none
  Preempt:                      enabled

  Sync-group:                   TEST

  VIP count:                    1
    10.10.1.100/32

Interface: dp0p1s2
--------------
  Group: 1
  ----------
  State:                        MASTER
  Last transition:              3s

  Version:                      2
  Configured Priority:          200
  Effective Priority:           200
  Advertisement interval:       1 sec
  Authentication type:          none
  Preempt:                      enabled

  Sync-group:                   TEST

  VIP count:                    1
    10.10.2.100/32

"""


@pytest.fixture
def no_sync_group_show_sync():
    return """
--------------------------------------------------
"""


@pytest.fixture
def multiple_sync_group_show_sync():
    return """
--------------------------------------------------
Group: TEST
---------
  State: MASTER
  Monitoring:
    Interface: dp0p1s1, Group: 1
    Interface: dp0p1s2, Group: 1

Group: TESTV2
---------
  State: MASTER
  Monitoring:
    Interface: dp0p1s3, Group: 1
    Interface: dp0p1s4, Group: 1

"""


@pytest.fixture
def sync_group_show_sync_group_filter():
    return """
--------------------------------------------------
Group: TESTV2
---------
  State: MASTER
  Monitoring:
    Interface: dp0p1s3, Group: 1
    Interface: dp0p1s4, Group: 1

"""


@pytest.fixture
def sync_group_show_sync_group_filter_no_group():
    return """
Sync-group: TEST1 does not exist
"""


@pytest.fixture
def multiple_sync_group_simple_keepalived_state():
    return \
        {
            "sync-groups":
            [
                {
                    "name": "TEST",
                    "state": "MASTER",
                    "members": [
                        "vyatta-dp0p1s2-1",
                        "vyatta-dp0p1s1-1"
                    ]
                },
                {
                    "name": "TESTV2",
                    "state": "MASTER",
                    "members": [
                        "vyatta-dp0p1s3-1",
                        "vyatta-dp0p1s4-1"
                    ]
                }
            ]
        }


""" Show vrrp interface fixtures """


@pytest.fixture
def multiple_interfaces_and_groups_state(
        simple_config, instance_state, vrrp_yang_name,
        interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = [instance_state]

    dp0p1s2_state = {
        "tagnode": "dp0p1s2",
        vrrp_yang_name: {
            "vrrp-group": [
                {
                    "instance-state":
                    {
                        "address-owner": False,
                        "last-transition": 0,
                        "rfc-interface": "",
                        "state": "MASTER",
                        "sync-group": "",
                        "version": 2,
                        "src-ip": "10.10.1.1",
                        "base-priority": 100,
                        "effective-priority": 100,
                        "advert-interval": "2 sec",
                        "accept": True,
                        "preempt": True,
                        "auth-type": None,
                        "virtual-ips": [
                            "1.1.1.100/32"
                        ]
                    },
                    "tagnode": "2"
                },
                {
                    "instance-state":
                    {
                        "address-owner": False,
                        "last-transition": 0,
                        "rfc-interface": "",
                        "state": "MASTER",
                        "sync-group": "",
                        "version": 2,
                        "src-ip": "10.10.1.1",
                        "base-priority": 100,
                        "effective-priority": 100,
                        "advert-interval": "2 sec",
                        "accept": True,
                        "preempt": True,
                        "auth-type": None,
                        "virtual-ips": [
                            "2.2.2.100/32"
                        ]
                    },
                    "tagnode": "42"
                },
                {
                    "instance-state":
                    {
                        "address-owner": False,
                        "last-transition": 0,
                        "rfc-interface": "dp0vrrp1",
                        "state": "BACKUP",
                        "sync-group": "",
                        "version": 3,
                        "master-router": "10.10.1.2",
                        "master-priority": 100,
                        "src-ip": "10.10.1.1",
                        "base-priority": 50,
                        "effective-priority": 50,
                        "advert-interval": "2 sec",
                        "accept": True,
                        "preempt": True,
                        "auth-type": None,
                        "virtual-ips": [
                            "3.3.3.100/32"
                        ]
                    },
                    "tagnode": "200"
                }
            ]
        }
    }
    dp0p1s3_state = {
        "tagnode": "dp0p1s3",
        vrrp_yang_name: {
            "vrrp-group": [instance_state]
        }
    }
    dataplane_list.append(dp0p1s2_state)
    dataplane_list.append(dp0p1s3_state)
    return simple_yang_state


@pytest.fixture
def dp0p1s2_vrid_42_show_detail():
    return """
--------------------------------------------------
Interface: dp0p1s2
--------------
  Group: 42
  ----------
  State:                        MASTER
  Last transition:              3s

  Version:                      2
  Configured Priority:          100
  Effective Priority:           100
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled

  VIP count:                    1
    2.2.2.100/32

"""


@pytest.fixture
def dp0p1s2_full_show_detail():
    return """
--------------------------------------------------
Interface: dp0p1s2
--------------
  Group: 2
  ----------
  State:                        MASTER
  Last transition:              3s

  Version:                      2
  Configured Priority:          100
  Effective Priority:           100
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled

  VIP count:                    1
    1.1.1.100/32

  Group: 42
  ----------
  State:                        MASTER
  Last transition:              3s

  Version:                      2
  Configured Priority:          100
  Effective Priority:           100
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled

  VIP count:                    1
    2.2.2.100/32

  Group: 200
  ----------
  State:                        BACKUP
  Last transition:              3s

  Master router:                10.10.1.2
  Master priority:              100

  Version:                      3
  RFC Compliant                 
  Virtual MAC interface:        dp0vrrp1
  Address Owner:                no

  Source Address:               10.10.1.1
  Configured Priority:          50
  Effective Priority:           50
  Advertisement interval:       2 sec
  Preempt:                      enabled
  Accept:                       enabled

  VIP count:                    1
    3.3.3.100/32

"""  # noqa: W291


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
def instance_state_rfc_switch():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "sw0vrrp1",
                "state": "MASTER",
                "sync-group": "",
            },
            "tagnode": "1"
        }


@pytest.fixture
def instance_state_rfc_sync():
    return \
        {
            "instance-state":
            {
                "address-owner": False,
                "last-transition": 0,
                "rfc-interface": "dp0vrrp1",
                "state": "MASTER",
                "sync-group": "TEST",
            },
            "tagnode": "1"
        }


@pytest.fixture
def instance_state_rfc_ipao():
    return \
        {
            "instance-state":
            {
                "address-owner": True,
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
def route_to_track_group(route_to_yang_name):
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
                route_to_yang_name: [
                    {
                        "route": "10.10.10.128/25",
                        "weight": {
                            "type": "increment",
                            "value": 10
                        }
                    },
                    {
                        "route": "10.10.10.0/24",
                        "weight": {
                            "type": "decrement",
                            "value": 10
                        }
                    },
                    {
                        "route": "0.0.0.0/0"
                    }
                ]
            },
        }


@pytest.fixture
def max_config_group(pathmon_yang_name, route_to_yang_name):
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
                },
                route_to_yang_name: [
                    {"route": "10.10.10.0/24"}
                ]
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
def switch_rfc_group_keepalived_config():
    return """
vrrp_instance vyatta-sw0.10-1 {
    state BACKUP
    interface sw0.10
    virtual_router_id 1
    version 2
    start_delay 0
    priority 200
    advert_int 1
    virtual_ipaddress {
        10.10.1.100/25
    }
    use_vmac sw0vrrp1
    vmac_xmit_base
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
        route_to {
            10.10.10.0/24
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
def route_to_track_group_keepalived_config():
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
        route_to {
            10.10.10.128/25   weight  +10
            10.10.10.0/24   weight  -10
            0.0.0.0/0
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
def switch_vif_interface():
    return \
        {
            "tagnode": "sw0",
            "vif": [
                {
                    "tagnode": "10",
                    "vyatta-vrrp-v1:vrrp": {
                        "start-delay": 0
                    }
                }
            ],
            "vyatta-vrrp-v1:vrrp": {
                "start-delay": 0
            }
        }


@pytest.fixture
def vif_switch_list_sanitized(generic_group):
    switch_intf = \
        {
            "tagnode": "sw0.10",
            "vyatta-vrrp-v1:vrrp": {
                "start-delay": 0,
                "vrrp-group": [generic_group]
            }
        }
    return [switch_intf]


@pytest.fixture
def switch_list(switch_vif_interface):
    return [switch_vif_interface]


@pytest.fixture
def dataplane_list(dataplane_interface):
    return [dataplane_interface]


@pytest.fixture
def interface_yang_name():
    return "vyatta-interfaces-v1:interfaces"


@pytest.fixture
def switch_yang_name():
    return "vyatta-interfaces-switch-v1:switch"


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
def route_to_yang_name():
    return \
        "vyatta-vrrp-route-to-track-interfaces-dataplane-v1:route-to"


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
    simple_yang_config = copy.deepcopy(top_level_dictionary)
    simple_yang_config[interface_yang_name][dataplane_yang_name] =\
        copy.deepcopy(dataplane_list)
    return simple_yang_config


@pytest.fixture
def simple_state(simple_config, instance_state, vrrp_yang_name,
                 interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = [instance_state]
    return simple_yang_state


@pytest.fixture
def simple_rfc_state(simple_config, instance_state_rfc, vrrp_yang_name,
                     interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = [instance_state_rfc]
    return simple_yang_state


@pytest.fixture
def simple_rfc_sync_state(simple_config, instance_state_rfc_sync,
                          vrrp_yang_name, interface_yang_name,
                          dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = [instance_state_rfc_sync]
    return simple_yang_state


@pytest.fixture
def simple_rfc_ipao_state(simple_config, instance_state_rfc_ipao,
                          vrrp_yang_name, interface_yang_name,
                          dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = [instance_state_rfc_ipao]
    return simple_yang_state


@pytest.fixture
def simple_rfc_switch_state(simple_config, instance_state_rfc_switch,
                            vrrp_yang_name, interface_yang_name,
                            switch_yang_name, switch_list,
                            dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    del(simple_yang_state[interface_yang_name][dataplane_yang_name])
    del(switch_list[0]["vif"][0][vrrp_yang_name]["start-delay"])
    switch_list[0]["vif"][0]["tagnode"] = "sw0.10"
    switch_list[0]["vif"][0][vrrp_yang_name]["vrrp-group"] = \
        [instance_state_rfc_switch]
    simple_yang_state[interface_yang_name]["vif"] = \
        switch_list[0]["vif"]
    return simple_yang_state


@pytest.fixture
def detailed_simple_state(simple_config, detailed_simple_keepalived_state,
                          vrrp_yang_name, interface_yang_name,
                          dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_simple_rfc_state(simple_config,
                              detailed_rfc_simple_keepalived_state,
                              vrrp_yang_name,
                              interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_rfc_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_simple_rfc_sync_state(simple_config,
                                   detailed_rfc_sync_simple_keepalived_state,
                                   vrrp_yang_name, interface_yang_name,
                                   dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_rfc_sync_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_simple_rfc_ipao_state(simple_config,
                                   detailed_rfc_ipao_simple_keepalived_state,
                                   vrrp_yang_name, interface_yang_name,
                                   dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_rfc_ipao_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_backup_simple_state(
        simple_config, detailed_backup_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_backup_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_backup_track_intf_simple_state(
        simple_config, detailed_backup_track_intf_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_backup_track_intf_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_backup_track_intf_no_weight_simple_state(
        simple_config,
        detailed_backup_track_intf_no_weight_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_backup_track_intf_no_weight_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_backup_track_pathmon_simple_state(
        simple_config,
        detailed_backup_track_pathmon_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_backup_track_pathmon_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_backup_track_route_simple_state(
        simple_config, detailed_backup_track_route_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_backup_track_route_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_v3_simple_state(simple_config,
                             detailed_v3_simple_keepalived_state,
                             vrrp_yang_name, interface_yang_name,
                             dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_v3_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_start_delay_simple_state(
        simple_config, detailed_start_delay_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name,
        dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_start_delay_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_preempt_delay_simple_state(
        simple_config, detailed_preempt_delay_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name,
        dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_preempt_delay_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_simple_multi_sync_state(
        simple_config,
        detailed_multi_group_first_simple_keepalived_state,
        second_dataplane_interface,
        detailed_multi_group_second_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name,
        dataplane_yang_name, sync_group_simple_keepalived_state):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    dataplane_list.append(second_dataplane_interface)
    del(dataplane_list[0][vrrp_yang_name]["start-delay"])
    del(dataplane_list[1][vrrp_yang_name]["start-delay"])
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_multi_group_first_simple_keepalived_state]
    dataplane_list[1][vrrp_yang_name]["vrrp-group"] = \
        [detailed_multi_group_second_simple_keepalived_state]
    simple_yang_state[vrrp_yang_name] = sync_group_simple_keepalived_state
    return simple_yang_state


@pytest.fixture
def simple_sync_group_state(
        simple_config, vrrp_yang_name, interface_yang_name,
        sync_group_simple_keepalived_state):
    simple_yang_state = copy.deepcopy(simple_config)
    del(simple_yang_state[interface_yang_name])
    simple_yang_state[vrrp_yang_name] = sync_group_simple_keepalived_state
    return simple_yang_state


@pytest.fixture
def multiple_simple_sync_group_state(
        simple_config, vrrp_yang_name, interface_yang_name,
        multiple_sync_group_simple_keepalived_state):
    simple_yang_state = copy.deepcopy(simple_config)
    del(simple_yang_state[interface_yang_name])
    simple_yang_state[vrrp_yang_name] = \
        multiple_sync_group_simple_keepalived_state
    return simple_yang_state


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
def simple_switch_config(
        top_level_dictionary, interface_yang_name, switch_yang_name,
        switch_list):
    simple_yang_config = top_level_dictionary
    simple_yang_config[interface_yang_name][switch_yang_name] = \
        switch_list
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

        def SendGarp(self):  # noqa: N802
            return {}

        @SubState.setter
        def SubState(self, new_state):  # noqa: N802
            self._state = new_state

        def GetRfcMapping(self, intf: str):  # noqa: N802
            if "vrrp" in intf:
                return ("dp0p1s1", 1)
            return ("", 0)

        def __getitem__(self, name):
            return PropertyInterface()

    class MockSystemBus:

        def __init__(self):
            pass

        def get(self, obj_name, obj_path):

            if "/org/freedesktop/systemd1/unit/" + \
                    "vyatta_2dkeepalived_2eservice" == obj_path or \
                    "org.keepalived.Vrrp1" == obj_name or \
                    "org.keepalived.Vrrp1.Instance" == obj_name:
                vrrp_proxy = VrrpProxyObject()
                return vrrp_proxy
            if "/org/freedesktop/systemd1" == obj_path:
                systemd = SystemdProxyObject()
                return systemd

        def watch_name(self, name, name_appeared=None):
            return

    monkeypatch.setitem(pydbus.__dict__, "SystemBus", MockSystemBus)
    return PropertyInterface


@pytest.fixture
def mock_pydbus_rfc(mock_pydbus):
    def GetAllRfc(self, interface_name):  # noqa: N802
        return {'Name': ("vyatta-dp0p1s1-1",),
                "SyncGroup": ("",),
                "XmitIntf": ("dp0vrrp1",),
                "State": (2, "Master"),
                "LastTransition": (0,),
                "AddressOwner": (False,)
                }
    mock_pydbus.GetAll = GetAllRfc


@pytest.fixture
def mock_snmp_config(tmp_path):
    config_string = """
# autogenerated by vyatta-snmp.pl on Tue Jun  4 13:38:55 2019
sysDescr Vyatta 18.3.0-Master
sysServices 14
master agentx
agentXSocket udp:localhost:100
agentaddress unix:/var/run/snmpd.socket,udp:161,udp6:161
agentgroup vyattacfg
agentXTimeout 5
pass_persist .1.3.6.1.2.1.123.1 /opt/vyatta/sbin/vyatta-nat-mib.pl
pass_persist .1.3.6.1.4.1.74.1.32.1 /opt/vyatta/sbin/vyattaqosmib.pl
pass_persist .1.3.6.1.4.1.74.1.32.4 /opt/vyatta/sbin/vyatta-storm-ctl-mib.pl
rocommunity public
rocommunity6 public
sysObjectID 1.3.6.1.4.1.74.1.32
syscontact Unknown
disablesnmpv3 true
#contexts
#             context contextID

iquerySecName vyatta0294fc9207f93c9b
notificationEvent  linkUpTrap    linkUp   ifIndex ifName ifAlias ifType ifAdminStatus ifOperStatus
notificationEvent  linkDownTrap  linkDown ifIndex ifName ifAlias ifType ifAdminStatus ifOperStatus
monitor  -r 10 -e linkUpTrap   "Generate linkUp" ifOperStatus != 2
monitor  -r 10 -e linkDownTrap "Generate linkDown" ifOperStatus == 2
# views

# overrides
override .1.3.6.1.2.1.80.1.2.1.13.3 octet_str ""

"""  # noqa: E501
    file_path = f"{tmp_path}/snmpd.conf"
    with open(file_path, "w") as file_handle:
        file_handle.write(config_string)
