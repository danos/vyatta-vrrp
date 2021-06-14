# Copyright (c) 2019-2021 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only.

import sys
import socket
import copy
import pytest

from vyatta.vrrp_vci.keepalived.vrrp import VrrpGroup

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

    sys.modules["gi.repository"] = FakeGi
    sys.modules["gi.repository.GLib"] = FakeGi.GLib


@pytest.fixture
def calendar_fakes(monkeypatch):

    # pylint: disable=import-outside-toplevel
    import vyatta.vrrp_vci.show_vrrp_cmds
    # import time and monkeypatch here so the version used by the
    # runner doesn't get messed up

    def fake_time():
        return 3
    monkeypatch.setattr(vyatta.vrrp_vci.show_vrrp_cmds.time, "time", fake_time)


@pytest.fixture
def socket_fakes():
    class FakeSocket:

        def __init__(self, family, sock_type):
            self.family = family
            self.sock_type = sock_type
            self.expected: str = ("127.0.0.1", "::1")

        def bind(self, connection):
            if connection[0] not in self.expected:
                raise OSError(
                    f"{connection[0]} not one of expected address: "
                    f"{self.expected}"
                )

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, exc_tb):
            pass

    setattr(socket, "socket", FakeSocket)


@pytest.fixture
def tmp_file_keepalived_config_no_write(tmp_path):
    class FakeVci:

        class Client:
            pass

    class FakeSubprocess:

        class Popen:

            def __init__(self, *args):
                self.pid = None
                return

    sys.modules["vci"] = FakeVci
    sys.modules["subprocess"] = FakeSubprocess
    from vyatta.vrrp_vci.keepalived.config_file import KeepalivedConfig
    file_path = f"{tmp_path}/keepalived.conf"
    return KeepalivedConfig(file_path)


@pytest.fixture
def test_config(
        pydbus_fakes, tmp_path,
        tmp_file_keepalived_config_no_write
):

    class FakeVci:

        class Config:
            pass

        class State:
            pass

    class VciException(Exception):
        def __init__(self, namespace, message, path, *args):
            self.name = namespace
            self.message = message
            self.path = path
            self.arg = args
            super().__init__(message)

    setattr(
        FakeVci, "Exception", VciException
    )

    sys.modules["vci"] = FakeVci
    import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl

    class MockProcess(process_ctrl.ProcessControl):

        def __init__(self):
            super().__init__()
            self.systemd_default_file_path = \
                f"{tmp_path}/vyatta-keepalived"
            self.snmpd_conf_file_path = \
                f"{tmp_path}/snmpd.conf"
    setattr(process_ctrl, "ProcessControl", MockProcess)
    from vyatta.vrrp_vci.vyatta_vrrp_vci import Config
    return Config(tmp_file_keepalived_config_no_write)


@pytest.fixture
def test_state(tmp_file_keepalived_config_no_write):
    class FakeVci:

        class Client:
            pass

    sys.modules["vci"] = FakeVci
    from vyatta.vrrp_vci.vyatta_vrrp_vci import State
    return State(tmp_file_keepalived_config_no_write)


@pytest.fixture
def test_state_vif(tmp_file_keepalived_config_no_write):
    class FakeVci:
        class Client:
            pass

    sys.modules["vci"] = FakeVci
    from vyatta.vrrp_vci.vyatta_vrrp_vci import State
    return State(tmp_file_keepalived_config_no_write)


@pytest.fixture
def keepalived_config(pydbus_fakes):
    class FakeVci:
        class Client:
            pass

    sys.modules["vci"] = FakeVci
    from vyatta.vrrp_vci.keepalived.config_file import KeepalivedConfig
    return KeepalivedConfig()


@pytest.fixture
def tmp_file_keepalived_config(tmp_path, autogeneration_string,
                               dataplane_group_keepalived_config):
    class FakeVci:

        class Client:
            pass

    sys.modules["vci"] = FakeVci
    from vyatta.vrrp_vci.keepalived.config_file import KeepalivedConfig
    file_path = f"{tmp_path}/keepalived.conf"
    with open(file_path, "w") as file_handle:
        file_handle.write(
            (
                autogeneration_string +
                dataplane_group_keepalived_config
            )
        )
    return KeepalivedConfig(file_path)


@pytest.fixture
def tmp_file_keepalived_vif_config(
        tmp_path, autogeneration_string,
        dataplane_vif_group_keepalived_config):
    class FakeVci:

        class Client:
            pass

    sys.modules["vci"] = FakeVci
    from vyatta.vrrp_vci.keepalived.config_file import KeepalivedConfig
    file_path = f"{tmp_path}/keepalived.conf"
    with open(file_path, "w") as file_handle:
        file_handle.write(
            (
                autogeneration_string +
                dataplane_vif_group_keepalived_config
            )
        )
    return KeepalivedConfig(file_path)


@pytest.fixture
def tmp_file_syncgroup_keepalived_config(
        tmp_path, syncgroup_keepalived_config):
    class FakeVci:

        class Client:
            pass

    sys.modules["vci"] = FakeVci
    from vyatta.vrrp_vci.keepalived.config_file import KeepalivedConfig
    file_path = f"{tmp_path}/keepalived.conf"
    with open(file_path, "w") as file_handle:
        file_handle.write(syncgroup_keepalived_config)
    return KeepalivedConfig(file_path)


@pytest.fixture
def non_default_keepalived_config():
    class FakeVci:

        class Client:
            pass

    sys.modules["vci"] = FakeVci
    from vyatta.vrrp_vci.keepalived.config_file import KeepalivedConfig
    return KeepalivedConfig("/test/file/path.conf")


@pytest.fixture
def simple_vrrp_group_object(generic_group):
    new_group = copy.deepcopy(generic_group)
    return VrrpGroup("dp0p1s1", "0", new_group)


@pytest.fixture
def fuller_vrrp_group_object(max_config_group):
    new_group = copy.deepcopy(max_config_group)
    return VrrpGroup("dp0p1s1", "0", new_group, 1)


"""Show vrrp fixtures"""


@pytest.fixture
def generic_group():
    return {
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
def modified_vif_group():
    return {
        "accept": False,
        "preempt": True,
        "tagnode": 2,
        "version": 2,
        "virtual-address": [
            "10.10.2.100/25"
        ]
    }


@pytest.fixture
def generic_rfc_group():
    return {
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
    return {
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
def generic_group_vif_show_summary():
    return """
                                 RFC        Addr   Last        Sync
Interface         Group  State   Compliant  Owner  Transition  Group
---------         -----  -----   ---------  -----  ----------  -----
dp0p1s1.10        1      MASTER  no         no     3s          <none>

"""


"""Show vrrp detail fixtures"""


@pytest.fixture
def generic_group_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 100
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
    return {
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
   Interface = dp0vrrp1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 100
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
    return {
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
   Interface = dp0vrrp1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 100
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
   monitor = vyatta-dp0p1s2-1
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
    return {
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
   Interface = dp0vrrp1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 100
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
    return {
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
   Master priority = 100
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.2
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 50
   Effective priority = 50
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/24 dev dp0p1s1 scope global
    """


@pytest.fixture
def multiple_group_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s2-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s2
   Interface = dp0vrrp1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 100
   Effective priority = 255
   Address owner = yes
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0vrrp1 scope global
 VRRP Instance = vyatta-dp0p1s2-42
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s2
   Interface = dp0p1s2
   Using src_ip = 10.10.1.2
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 42
   Priority = 100
   Effective priority = 100
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     2.2.2.100/32 dev dp0p1s2 scope global
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
    return {
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
            "src-ip": "10.10.1.2",
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
   Master priority = 100
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.2
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 50
   Effective priority = 50
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Tracked interfaces = 1
     name dp0s2 state UP weight -10
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
    return {
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
            "src-ip": "10.10.1.2",
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
def backup_generic_group_track_intf_down_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = BACKUP
   Master router = 10.10.1.1
   Master priority = 100
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.2
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 50
   Effective priority = 50
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Tracked interfaces = 1
     name dp0s2 state DOWN weight -10
   Virtual IP = 1
     10.10.1.100/24 dev dp0p1s1 scope global
    """


@pytest.fixture
def detailed_backup_generic_group_track_intf_down_show_detail():
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
    dp0s2   state DOWN      weight -10
  VIP count:                    1
    10.10.1.100/24

"""


@pytest.fixture
def detailed_backup_track_intf_down_simple_keepalived_state():
    return {
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
            "src-ip": "10.10.1.2",
            "base-priority": 50,
            "effective-priority": 50,
            "advert-interval": "2 sec",
            "accept": True,
            "preempt": True,
            "auth-type": None,
            "track": {
                "interface": [
                    {
                        "name": "dp0s2", "state": "DOWN",
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
   Master priority = 100
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.2
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 50
   Effective priority = 50
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Tracked interfaces = 1
     name dp0s2 state UP weight 0
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
    return {
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
            "src-ip": "10.10.1.2",
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
   Master priority = 100
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.2
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 50
   Effective priority = 50
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Tracked path-monitors = 1
     name test_monitor/test_policy state UP weight 10
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
    return {
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
            "src-ip": "10.10.1.2",
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
def backup_generic_group_multiple_track_pathmon_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = BACKUP
   Master router = 10.10.1.1
   Master priority = 100
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.2
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 50
   Effective priority = 50
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Tracked path-monitors = 2
     name test_monitor/test_policy state UP weight 10
     name test_monitor/test_nonpolicy state UP weight 0
   Virtual IP = 1
     10.10.1.100/24 dev dp0p1s1 scope global
    """


@pytest.fixture
def detailed_backup_generic_group_multiple_track_pathmon_show_detail():
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
      test_nonpolicy COMPLIANT
      test_policy  COMPLIANT  weight 10
  VIP count:                    1
    10.10.1.100/24

"""  # noqa: W291


@pytest.fixture
def detailed_backup_multiple_track_pathmon_simple_keepalived_state():
    return {
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
            "src-ip": "10.10.1.2",
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
                            },
                            {
                                "name": "test_nonpolicy",
                                "state": "COMPLIANT",
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
   Master priority = 100
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.2
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 50
   Effective priority = 50
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Tracked routes = 1
     name 10.10.10.0/24 state DOWN weight 10
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
    return {
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
            "src-ip": "10.10.1.2",
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
def generic_group_track_multiple_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 50
   Effective priority = 70
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Tracked interfaces = 2
      name dp0p1s1 state UP weight 10
      name dp0s2 state UP weight 0
   Tracked path-monitors = 2
      name test_monitor/test_policy state UP weight 10
      name test_monitor/test_nonpolicy state UP weight 0
   Tracked routes = 2
     name 10.10.10.0/24 state DOWN weight 10
     name 11.11.11.0/24 state UP weight 0
   Virtual IP = 1
     10.10.1.100/24 dev dp0p1s1 scope global
    """


@pytest.fixture
def detailed_generic_group_track_multiple_show_detail():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        MASTER
  Last transition:              3s

  Version:                      2
  Configured Priority:          50
  Effective Priority:           70
  Advertisement interval:       2 sec
  Authentication type:          none
  Preempt:                      enabled

  Tracked Interfaces count:     2
    dp0p1s1   state UP      weight 10
    dp0s2   state UP
  Tracked Path Monitor count:   2
    test_monitor
      test_nonpolicy  COMPLIANT
      test_policy  COMPLIANT  weight 10
  Tracked routes count:         2
    10.10.10.0/24   state DOWN      weight 10
    11.11.11.0/24   state UP
  VIP count:                    1
    10.10.1.100/24

"""


@pytest.fixture
def detailed_track_multiple_simple_keepalived_state():
    return {
        "instance-state":
        {
            "address-owner": False,
            "last-transition": 0,
            "rfc-interface": "",
            "state": "MASTER",
            "sync-group": "",
            "version": 2,
            "src-ip": "10.10.1.1",
            "base-priority": 50,
            "effective-priority": 70,
            "advert-interval": "2 sec",
            "accept": True,
            "preempt": True,
            "auth-type": None,
            "track": {
                "interface": [
                    {
                        "name": "dp0p1s1", "state": "UP",
                        "weight": "10"
                    },
                    {
                        "name": "dp0s2", "state": "UP"
                    }
                ],
                "monitor": [
                    {
                        "name": "test_monitor",
                        "policies": [
                            {
                                "name": "test_policy",
                                "state": "COMPLIANT",
                                "weight": "10"
                            },
                            {
                                "name": "test_nonpolicy",
                                "state": "COMPLIANT",
                            }
                        ]
                    }
                ],
                "route": [
                    {
                        "name": "10.10.10.0/24",
                        "state": "DOWN",
                        "weight": "10"
                    },
                    {
                        "name": "11.11.11.0/24",
                        "state": "UP"
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
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 100
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
    return {
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
            "accept": False,
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
  Accept:                       disabled

  VIP count:                    1
    10.10.1.100/32

"""


@pytest.fixture
def generic_v3_rfc_group_fast_advert_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 3
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Interface = dp0vrrp1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 100
   Effective priority = 100
   Address owner = no
   Advert interval = 500 milli-sec
   Accept = disabled
   Preempt = enabled
   Promote_secondaries = enabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0vrrp1 scope global
"""


@pytest.fixture
def detailed_v3_rfc_fast_advert_simple_keepalived_state():
    return {
        "instance-state":
        {
            "address-owner": False,
            "last-transition": 0,
            "rfc-interface": "dp0vrrp1",
            "state": "MASTER",
            "sync-group": "",
            "version": 3,
            "src-ip": "10.10.1.1",
            "base-priority": 100,
            "effective-priority": 100,
            "advert-interval": "500 milli-sec",
            "accept": False,
            "preempt": True,
            "auth-type": None,
            "virtual-ips": [
                "10.10.1.100/32"
            ]
        },
        "tagnode": "1"
    }


@pytest.fixture
def generic_v3_rfc_group_fast_advert_show_detail():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  State:                        MASTER
  Last transition:              3s

  Version:                      3
  RFC Compliant                 
  Virtual MAC interface:        dp0vrrp1
  Address Owner:                no

  Source Address:               10.10.1.1
  Configured Priority:          100
  Effective Priority:           100
  Advertisement interval:       500 milli-sec
  Preempt:                      enabled
  Accept:                       disabled

  VIP count:                    1
    10.10.1.100/32

"""  # noqa: W291


@pytest.fixture
def generic_group_start_delay_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 100
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
    return {
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
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 100
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
    return {
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


@pytest.fixture
def generic_group_vif_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1.10-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1.10
   Interface = dp0p1s1.10
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 100
   Effective priority = 100
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0p1s1.10 scope global
"""


@pytest.fixture
def detailed_simple_vif_keepalived_state():
    return {
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
def generic_group_vif_show_detail():
    return """
--------------------------------------------------
Interface: dp0p1s1.10
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
def generic_group_vif_and_parent_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 100
   Effective priority = 100
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0p1s1 scope global
 VRRP Instance = vyatta-dp0p1s1.10-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:00 1970)
   Listening device = dp0p1s1.10
   Interface = dp0p1s1.10
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 100
   Effective priority = 100
   Address owner = no
   Advert interval = 2 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0p1s1.10 scope global
"""


"""Show vrrp sync group fixtures"""


@pytest.fixture
def sync_group_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 200
   Effective priority = 200
   Address owner = no
   Advert interval = 1 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0p1s1 scope global
 VRRP Instance = vyatta-dp0p1s2-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s2
   Interface = dp0p1s2
   Using src_ip = 10.10.2.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 200
   Effective priority = 200
   Address owner = no
   Advert interval = 1 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.2.100/32 dev dp0p1s2 scope global
------< VRRP Sync groups >------
 VRRP Sync Group = TEST, MASTER
   monitor = vyatta-dp0p1s2-1
   monitor = vyatta-dp0p1s1-1
"""


@pytest.fixture
def sync_group_simple_keepalived_state():
    return {
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
    return {
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
    return {
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
def multiple_sync_groups_simple_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s1
   Interface = dp0p1s1
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 200
   Effective priority = 200
   Address owner = no
   Advert interval = 1 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0p1s1 scope global
 VRRP Instance = vyatta-dp0p1s2-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s2
   Interface = dp0p1s2
   Using src_ip = 10.10.2.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 200
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
   Interface = dp0p1s3
   Using src_ip = 10.10.3.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 200
   Effective priority = 200
   Address owner = no
   Advert interval = 1 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0p1s3 scope global
 VRRP Instance = vyatta-dp0p1s4-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s4
   Interface = dp0p1s4
   Using src_ip = 10.10.4.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 200
   Effective priority = 200
   Address owner = no
   Advert interval = 1 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.2.100/32 dev dp0p1s4 scope global
------< VRRP Sync groups >------
 VRRP Sync Group = TEST, MASTER
   monitor = vyatta-dp0p1s2-1
   monitor = vyatta-dp0p1s1-1
 VRRP Sync Group = TESTV2, MASTER
   monitor = vyatta-dp0p1s3-1
   monitor = vyatta-dp0p1s4-1

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
def sync_group_simple_vif_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1.10-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s1.10
   Interface = dp0p1s1.10
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 200
   Effective priority = 200
   Address owner = no
   Advert interval = 1 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0p1s1 scope global
 VRRP Instance = vyatta-dp0p1s2.20-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s2.20
   Interface = dp0p1s2.20
   Using src_ip = 10.10.2.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 200
   Effective priority = 200
   Address owner = no
   Advert interval = 1 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.2.100/32 dev dp0p1s2 scope global
------< VRRP Sync groups >------
 VRRP Sync Group = TEST, MASTER
   monitor = vyatta-dp0p1s2.20-1
   monitor = vyatta-dp0p1s1.10-1
"""


@pytest.fixture
def sync_group_simple_vif_keepalived_state():
    return {
        "sync-groups":
        [
            {
                "name": "TEST",
                "state": "MASTER",
                "members": [
                    "vyatta-dp0p1s2.20-1",
                    "vyatta-dp0p1s1.10-1"
                ]
            }
        ]
    }


@pytest.fixture
def generic_sync_group_vif_show_sync():
    return """
--------------------------------------------------
Group: TEST
---------
  State: MASTER
  Monitoring:
    Interface: dp0p1s1.10, Group: 1
    Interface: dp0p1s2.20, Group: 1

"""


@pytest.fixture
def sync_group_simple_vif_and_nonvif_keepalived_data():
    return """
------< VRRP Topology >------
 VRRP Instance = vyatta-dp0p1s1.10-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s1.10
   Interface = dp0p1s1.10
   Using src_ip = 10.10.1.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 200
   Effective priority = 200
   Address owner = no
   Advert interval = 1 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.1.100/32 dev dp0p1s1.10 scope global
 VRRP Instance = vyatta-dp0p1s2.20-1
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s2.20
   Interface = dp0p1s2.20
   Using src_ip = 10.10.2.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 1
   Priority = 200
   Effective priority = 200
   Address owner = no
   Advert interval = 1 sec
   Accept = enabled
   Preempt = enabled
   Promote_secondaries = disabled
   Authentication type = none
   Virtual IP = 1
     10.10.2.100/32 dev dp0p1s2.20 scope global
 VRRP Instance = vyatta-dp0p1s3-42
 VRRP Version = 2
   State = MASTER
   Last transition = 0 (Thur Jan 1 00:00:03 1970)
   Listening device = dp0p1s3
   Interface = dp0p1s3
   Using src_ip = 10.10.3.1
   Gratuitous ARP delay = 5
   Gratuitous ARP repeat = 5
   Gratuitous ARP refresh = 0
   Gratuitous ARP refresh repeat = 1
   Gratuitous ARP lower priority delay = 5
   Gratuitous ARP lower priority repeat = 5
   Send advert after receive lower priority advert = true
   Virtual Router ID = 42
   Priority = 200
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
   monitor = vyatta-dp0p1s2.20-1
   monitor = vyatta-dp0p1s1.10-1
   monitor = vyatta-dp0p1s3-42
"""


@pytest.fixture
def generic_sync_group_vif_and_nonvif_show_sync():
    return """
--------------------------------------------------
Group: TEST
---------
  State: MASTER
  Monitoring:
    Interface: dp0p1s1.10, Group: 1
    Interface: dp0p1s2.20, Group: 1
    Interface: dp0p1s3, Group: 42

"""


"""Show vrrp statistics fixtures"""


@pytest.fixture
def generic_group_keepalived_stats():
    return """
VRRP Instance: vyatta-dp0p1s1-1
  Advertisements:
    Received: 0
    Sent: 615
  Became master: 1
  Released master: 0
  Packet Errors:
    Length: 0
    TTL: 0
    Invalid Type: 0
    Advertisement Interval: 0
    Address List: 0
  Authentication Errors:
    Invalid Type: 0
    Type Mismatch: 0
    Failure: 0
  Priority Zero:
    Received: 0
    Sent: 0
"""


@pytest.fixture
def generic_group_keepalived_stats_dict():
    return {
        "tagnode": 1,
        "stats": {
            "Advertisements": {
                "Received": "0",
                "Sent": "615"
            },
            "Became master": "1",
            "Released master": "0",
            "Packet errors": {
                "Length": "0",
                "TTL": "0",
                "Invalid type": "0",
                "Advertisement interval": "0",
                "Address list": "0"
            },
            "Authentication errors": {
                "Invalid type": "0",
                "Type mismatch": "0",
                "Failure": "0"
            },
            "Priority zero advertisements": {
                "Received": "0",
                "Sent": "0"
            }
        }
    }


@pytest.fixture
def generic_group_show_stats():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  Advertisements:
    Received:                   0
    Sent:                       615

  Became master:                1
  Released master:              0

  Packet errors:
    Length:                     0
    TTL:                        0
    Invalid type:               0
    Advertisement interval:     0
    Address list:               0

  Authentication errors:
    Invalid type:               0
    Type mismatch:              0
    Failure:                    0

  Priority zero advertisements:
    Received:                   0
    Sent:                       0

"""


@pytest.fixture
def backup_group_keepalived_stats():
    return """
VRRP Instance: vyatta-dp0p1s1-42
  Advertisements:
    Received: 100
    Sent: 0
  Became master: 0
  Released master: 0
  Packet Errors:
    Length: 0
    TTL: 0
    Invalid Type: 0
    Advertisement Interval: 0
    Address List: 0
  Authentication Errors:
    Invalid Type: 0
    Type Mismatch: 0
    Failure: 0
  Priority Zero:
    Received: 0
    Sent: 0
"""


@pytest.fixture
def backup_group_keepalived_stats_dict():
    return {
        "tagnode": 42,
        "stats": {
            "Advertisements": {
                "Received": "100",
                "Sent": "0"
            },
            "Became master": "0",
            "Released master": "0",
            "Packet errors": {
                "Length": "0",
                "TTL": "0",
                "Invalid type": "0",
                "Advertisement interval": "0",
                "Address list": "0"
            },
            "Authentication errors": {
                "Invalid type": "0",
                "Type mismatch": "0",
                "Failure": "0"
            },
            "Priority zero advertisements": {
                "Received": "0",
                "Sent": "0"
            }
        }
    }


@pytest.fixture
def backup_group_show_stats():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 42
  ----------
  Advertisements:
    Received:                   100
    Sent:                       0

  Became master:                0
  Released master:              0

  Packet errors:
    Length:                     0
    TTL:                        0
    Invalid type:               0
    Advertisement interval:     0
    Address list:               0

  Authentication errors:
    Invalid type:               0
    Type mismatch:              0
    Failure:                    0

  Priority zero advertisements:
    Received:                   0
    Sent:                       0

"""


@pytest.fixture
def master_and_backup_group_keepalived_stats():
    return """
VRRP Instance: vyatta-dp0p1s1-1
  Advertisements:
    Received: 0
    Sent: 615
  Became master: 1
  Released master: 0
  Packet Errors:
    Length: 0
    TTL: 0
    Invalid Type: 0
    Advertisement Interval: 0
    Address List: 0
  Authentication Errors:
    Invalid Type: 0
    Type Mismatch: 0
    Failure: 0
  Priority Zero:
    Received: 0
    Sent: 0
VRRP Instance: vyatta-dp0p1s1-42
  Advertisements:
    Received: 100
    Sent: 0
  Became master: 0
  Released master: 0
  Packet Errors:
    Length: 0
    TTL: 0
    Invalid Type: 0
    Advertisement Interval: 0
    Address List: 0
  Authentication Errors:
    Invalid Type: 0
    Type Mismatch: 0
    Failure: 0
  Priority Zero:
    Received: 0
    Sent: 0
"""


@pytest.fixture
def master_and_backup_group_show_stats():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  Advertisements:
    Received:                   0
    Sent:                       615

  Became master:                1
  Released master:              0

  Packet errors:
    Length:                     0
    TTL:                        0
    Invalid type:               0
    Advertisement interval:     0
    Address list:               0

  Authentication errors:
    Invalid type:               0
    Type mismatch:              0
    Failure:                    0

  Priority zero advertisements:
    Received:                   0
    Sent:                       0

  Group: 42
  ----------
  Advertisements:
    Received:                   100
    Sent:                       0

  Became master:                0
  Released master:              0

  Packet errors:
    Length:                     0
    TTL:                        0
    Invalid type:               0
    Advertisement interval:     0
    Address list:               0

  Authentication errors:
    Invalid type:               0
    Type mismatch:              0
    Failure:                    0

  Priority zero advertisements:
    Received:                   0
    Sent:                       0

"""


@pytest.fixture
def second_intf_keepalived_stats_dict():
    return {
        "tagnode": 2,
        "stats": {
            "Advertisements": {
                "Received": "50",
                "Sent": "3305"
            },
            "Became master": "1",
            "Released master": "1",
            "Packet errors": {
                "Length": "0",
                "TTL": "0",
                "Invalid type": "0",
                "Advertisement interval": "0",
                "Address list": "0"
            },
            "Authentication errors": {
                "Invalid type": "0",
                "Type mismatch": "0",
                "Failure": "0"
            },
            "Priority zero advertisements": {
                "Received": "0",
                "Sent": "0"
            }
        }
    }


@pytest.fixture
def multiple_intf_keepalived_stats():
    return """
VRRP Instance: vyatta-dp0p1s1-1
  Advertisements:
    Received: 0
    Sent: 615
  Became master: 1
  Released master: 0
  Packet Errors:
    Length: 0
    TTL: 0
    Invalid Type: 0
    Advertisement Interval: 0
    Address List: 0
  Authentication Errors:
    Invalid Type: 0
    Type Mismatch: 0
    Failure: 0
  Priority Zero:
    Received: 0
    Sent: 0
VRRP Instance: vyatta-dp0p1s1-42
  Advertisements:
    Received: 100
    Sent: 0
  Became master: 0
  Released master: 0
  Packet Errors:
    Length: 0
    TTL: 0
    Invalid Type: 0
    Advertisement Interval: 0
    Address List: 0
  Authentication Errors:
    Invalid Type: 0
    Type Mismatch: 0
    Failure: 0
  Priority Zero:
    Received: 0
    Sent: 0
VRRP Instance: vyatta-dp0p1s2-2
  Advertisements:
    Received: 50
    Sent: 3305
  Became master: 1
  Released master: 1
  Packet Errors:
    Length: 0
    TTL: 0
    Invalid Type: 0
    Advertisement Interval: 0
    Address List: 0
  Authentication Errors:
    Invalid Type: 0
    Type Mismatch: 0
    Failure: 0
  Priority Zero:
    Received: 0
    Sent: 0
"""


@pytest.fixture
def multiple_intf_show_stats():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  Advertisements:
    Received:                   0
    Sent:                       615

  Became master:                1
  Released master:              0

  Packet errors:
    Length:                     0
    TTL:                        0
    Invalid type:               0
    Advertisement interval:     0
    Address list:               0

  Authentication errors:
    Invalid type:               0
    Type mismatch:              0
    Failure:                    0

  Priority zero advertisements:
    Received:                   0
    Sent:                       0

  Group: 42
  ----------
  Advertisements:
    Received:                   100
    Sent:                       0

  Became master:                0
  Released master:              0

  Packet errors:
    Length:                     0
    TTL:                        0
    Invalid type:               0
    Advertisement interval:     0
    Address list:               0

  Authentication errors:
    Invalid type:               0
    Type mismatch:              0
    Failure:                    0

  Priority zero advertisements:
    Received:                   0
    Sent:                       0

Interface: dp0p1s2
--------------
  Group: 2
  ----------
  Advertisements:
    Received:                   50
    Sent:                       3305

  Became master:                1
  Released master:              1

  Packet errors:
    Length:                     0
    TTL:                        0
    Invalid type:               0
    Advertisement interval:     0
    Address list:               0

  Authentication errors:
    Invalid type:               0
    Type mismatch:              0
    Failure:                    0

  Priority zero advertisements:
    Received:                   0
    Sent:                       0

"""


@pytest.fixture
def filtered_interface_and_group_show_stats():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 42
  ----------
  Advertisements:
    Received:                   100
    Sent:                       0

  Became master:                0
  Released master:              0

  Packet errors:
    Length:                     0
    TTL:                        0
    Invalid type:               0
    Advertisement interval:     0
    Address list:               0

  Authentication errors:
    Invalid type:               0
    Type mismatch:              0
    Failure:                    0

  Priority zero advertisements:
    Received:                   0
    Sent:                       0

"""


@pytest.fixture
def generic_group_vif_keepalived_stats():
    return """
VRRP Instance: vyatta-dp0p1s1.10-1
  Advertisements:
    Received: 0
    Sent: 615
  Became master: 1
  Released master: 0
  Packet Errors:
    Length: 0
    TTL: 0
    Invalid Type: 0
    Advertisement Interval: 0
    Address List: 0
  Authentication Errors:
    Invalid Type: 0
    Type Mismatch: 0
    Failure: 0
  Priority Zero:
    Received: 0
    Sent: 0
"""


@pytest.fixture
def generic_group_vif_keepalived_stats_dict():
    return {
        "tagnode": 1,
        "stats": {
            "Advertisements": {
                "Received": "0",
                "Sent": "615"
            },
            "Became master": "1",
            "Released master": "0",
            "Packet errors": {
                "Length": "0",
                "TTL": "0",
                "Invalid type": "0",
                "Advertisement interval": "0",
                "Address list": "0"
            },
            "Authentication errors": {
                "Invalid type": "0",
                "Type mismatch": "0",
                "Failure": "0"
            },
            "Priority zero advertisements": {
                "Received": "0",
                "Sent": "0"
            }
        }
    }


@pytest.fixture
def generic_group_vif_show_stats():
    return """
--------------------------------------------------
Interface: dp0p1s1.10
--------------
  Group: 1
  ----------
  Advertisements:
    Received:                   0
    Sent:                       615

  Became master:                1
  Released master:              0

  Packet errors:
    Length:                     0
    TTL:                        0
    Invalid type:               0
    Advertisement interval:     0
    Address list:               0

  Authentication errors:
    Invalid type:               0
    Type mismatch:              0
    Failure:                    0

  Priority zero advertisements:
    Received:                   0
    Sent:                       0

"""


@pytest.fixture
def generic_group_vif_and_parent_show_stats():
    return """
--------------------------------------------------
Interface: dp0p1s1
--------------
  Group: 1
  ----------
  Advertisements:
    Received:                   0
    Sent:                       615

  Became master:                1
  Released master:              0

  Packet errors:
    Length:                     0
    TTL:                        0
    Invalid type:               0
    Advertisement interval:     0
    Address list:               0

  Authentication errors:
    Invalid type:               0
    Type mismatch:              0
    Failure:                    0

  Priority zero advertisements:
    Received:                   0
    Sent:                       0

Interface: dp0p1s1.10
--------------
  Group: 1
  ----------
  Advertisements:
    Received:                   0
    Sent:                       615

  Became master:                1
  Released master:              0

  Packet errors:
    Length:                     0
    TTL:                        0
    Invalid type:               0
    Advertisement interval:     0
    Address list:               0

  Authentication errors:
    Invalid type:               0
    Type mismatch:              0
    Failure:                    0

  Priority zero advertisements:
    Received:                   0
    Sent:                       0

"""


@pytest.fixture
def multiple_sync_group_simple_keepalived_state():
    return {
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
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
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
    return {
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
    return {
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
    return {
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
    return {
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
    return {
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
    return {
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
    return {
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
    return {
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
    return {
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
    return {
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
def generic_v3_fast_advert_group():
    return {
        "accept": False,
        "fast-advertise-interval": 500,
        "preempt": True,
        "tagnode": 1,
        "version": 3,
        "virtual-address": [
            "fe80::1/64",
            "2001::2/64",
        ]
    }


@pytest.fixture
def generic_v3_fast_advert_seconds_group():
    return {
        "accept": False,
        "fast-advertise-interval": 2000,
        "preempt": True,
        "tagnode": 1,
        "version": 3,
        "virtual-address": [
            "fe80::1/64",
            "2001::2/64",
        ]
    }


@pytest.fixture
def generic_v3_fast_advert_between_seconds_group():
    return {
        "accept": False,
        "fast-advertise-interval": 2500,
        "preempt": True,
        "tagnode": 1,
        "version": 3,
        "virtual-address": [
            "fe80::1/64",
            "2001::2/64",
        ]
    }


@pytest.fixture
def runtransition_v3_group():
    return {
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
    return {
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
    return {
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
    return {
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
    return {
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
    return {
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
    return {
        "accept": False,
        "advertise-interval": 2,
        "authentication": {
            "password": "help",
            "type": "plaintext-password"
        },
        "hello-source-address": "127.0.0.1",
        "notify": {
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
def bonding_max_config_group(
    bonding_pathmon_yang_name, bonding_route_to_yang_name
):
    return {
        "accept": False,
        "advertise-interval": 2,
        "authentication": {
            "password": "help",
            "type": "plaintext-password"
        },
        "hello-source-address": "127.0.0.1",
        "notify": {
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
            bonding_pathmon_yang_name: {
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
            bonding_route_to_yang_name: [
                {"route": "10.10.10.0/24"}
            ]
        },
        "version": 2,
        "virtual-address": [
            "10.10.1.100/25"
        ]
    }


@pytest.fixture
def switch_max_config_group(
    switch_pathmon_yang_name, switch_route_to_yang_name
):
    return {
        "accept": False,
        "advertise-interval": 2,
        "authentication": {
            "password": "help",
            "type": "plaintext-password"
        },
        "hello-source-address": "127.0.0.1",
        "notify": {
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
            switch_pathmon_yang_name: {
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
            switch_route_to_yang_name: [
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
    return {
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
    return {
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
    return {
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
    return {
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
def sync_group3():
    return {
        "accept": False,
        "preempt": True,
        "priority": 200,
        "sync-group": "TESTV2",
        "tagnode": 1,
        "version": 2,
        "virtual-address": [
            "10.10.1.100"
        ]
    }


@pytest.fixture
def sync_group4():
    return {
        "accept": False,
        "preempt": True,
        "priority": 200,
        "sync-group": "TESTV2",
        "tagnode": 1,
        "version": 2,
        "virtual-address": [
            "10.10.2.100"
        ]
    }


@pytest.fixture
def syncgroup1_dataplane_interface(sync_group1):
    return {
        "tagnode": "dp0p1s1",
        "vyatta-vrrp-v1:vrrp": {
            "start-delay": 0,
            "vrrp-group": [sync_group1]
        }
    }


@pytest.fixture
def syncgroup2_dataplane_interface(sync_group2):
    return {
        "tagnode": "dp0p1s2",
        "vyatta-vrrp-v1:vrrp": {
            "start-delay": 0,
            "vrrp-group": [sync_group2]
        }
    }


@pytest.fixture
def syncgroup3_dataplane_interface(sync_group3):
    return {
        "tagnode": "dp0p1s3",
        "vyatta-vrrp-v1:vrrp": {
            "start-delay": 0,
            "vrrp-group": [sync_group3]
        }
    }


@pytest.fixture
def syncgroup4_dataplane_interface(sync_group4):
    return {
        "tagnode": "dp0p1s4",
        "vyatta-vrrp-v1:vrrp": {
            "start-delay": 0,
            "vrrp-group": [sync_group4]
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
    no_accept
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
    no_accept
}"""


@pytest.fixture
def syncgroup3_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s3-1 {
    state BACKUP
    interface dp0p1s3
    virtual_router_id 1
    version 2
    start_delay 0
    priority 200
    advert_int 1
    virtual_ipaddress {
        10.10.1.100
    }
    no_accept
}"""


@pytest.fixture
def syncgroup4_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s4-1 {
    state BACKUP
    interface dp0p1s4
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
    sync_group_tracking_weight
}
"""


@pytest.fixture
def second_syncgroup_keepalived_section():
    return """
vrrp_sync_group TESTV2 {
    group {
        vyatta-dp0p1s3-1
        vyatta-dp0p1s4-1
    }
    sync_group_tracking_weight
}
"""


@pytest.fixture
def dataplane_interface(generic_group):
    return {
        "tagnode": "dp0p1s1",
        "vyatta-vrrp-v1:vrrp": {
            "start-delay": 0,
            "vrrp-group": [copy.deepcopy(generic_group)]
        }
    }


@pytest.fixture
def syncgroup_dataplane_list(
        syncgroup1_dataplane_interface,
        syncgroup2_dataplane_interface):
    return [syncgroup1_dataplane_interface, syncgroup2_dataplane_interface]


@pytest.fixture
def multiple_syncgroup_dataplane_list(
        syncgroup1_dataplane_interface,
        syncgroup2_dataplane_interface,
        syncgroup3_dataplane_interface,
        syncgroup4_dataplane_interface):
    return [
        syncgroup1_dataplane_interface, syncgroup2_dataplane_interface,
        syncgroup3_dataplane_interface, syncgroup4_dataplane_interface
    ]


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
    no_accept
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
    no_accept
    use_vmac sw0vrrp1
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
    no_accept
    track_interface {
        dp0p1s1   weight  +10
        dp0s2   weight  -10
        lo
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
    no_accept
    track_interface {
        dp0p1s1
        lo
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
    no_accept
    track_interface {
        lo
    }
    track_pathmon {
        test_monitor/test_policy
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
    no_accept
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
    no_accept
}"""


@pytest.fixture
def generic_v3_fast_advert_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 3
    start_delay 0
    priority 100
    advert_int 0.5
    virtual_ipaddress {
        fe80::1/64
        2001::2/64
    }
    native_ipv6
    no_accept
}"""


@pytest.fixture
def generic_v3_fast_advert_group_seconds_keepalived_config():
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
    no_accept
}"""


@pytest.fixture
def generic_v3_fast_advert_group_between_seconds_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 3
    start_delay 0
    priority 100
    advert_int 2.5
    virtual_ipaddress {
        fe80::1/64
        2001::2/64
    }
    native_ipv6
    no_accept
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
    no_accept
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
    no_accept
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
    no_accept
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
    no_accept
    use_vmac dp0vrrp1
    preempt_delay 10
    mcast_src_ip 127.0.0.1
    authentication {
        auth_type PASS
        auth_pass help
    }
    track_interface {
        dp0p1s1   weight  +10
        dp0s2   weight  -10
        lo
    }
    track_pathmon {
        test_monitor/test_policy      weight  -10
    }
    track_route_to {
        10.10.10.0/24
    }
    notify    /opt/vyatta/sbin/vyatta-ipsec-notify.sh
}"""


@pytest.fixture
def bonding_max_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0bond0-1 {
    state BACKUP
    interface dp0bond0
    virtual_router_id 1
    version 2
    start_delay 0
    priority 200
    advert_int 2
    virtual_ipaddress {
        10.10.1.100/25
    }
    no_accept
    use_vmac dp0vrrp1
    preempt_delay 10
    mcast_src_ip 127.0.0.1
    authentication {
        auth_type PASS
        auth_pass help
    }
    track_interface {
        dp0p1s1   weight  +10
        dp0s2   weight  -10
        lo
    }
    track_pathmon {
        test_monitor/test_policy      weight  -10
    }
    track_route_to {
        10.10.10.0/24
    }
    notify    /opt/vyatta/sbin/vyatta-ipsec-notify.sh
}"""


@pytest.fixture
def switch_max_group_keepalived_config():
    return """
vrrp_instance vyatta-sw0.10-1 {
    state BACKUP
    interface sw0.10
    virtual_router_id 1
    version 2
    start_delay 0
    priority 200
    advert_int 2
    virtual_ipaddress {
        10.10.1.100/25
    }
    no_accept
    use_vmac sw0vrrp1
    preempt_delay 10
    mcast_src_ip 127.0.0.1
    authentication {
        auth_type PASS
        auth_pass help
    }
    track_interface {
        dp0p1s1   weight  +10
        dp0s2   weight  -10
        lo
    }
    track_pathmon {
        test_monitor/test_policy      weight  -10
    }
    track_route_to {
        10.10.10.0/24
    }
    notify    /opt/vyatta/sbin/vyatta-ipsec-notify.sh
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
    no_accept
    track_pathmon {
        test_monitor/test_policy      weight  +10
        test_monitor/tester_policy      weight  -10
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
    no_accept
    track_route_to {
        10.10.10.128/25   weight  +10
        10.10.10.0/24   weight  -10
        0.0.0.0/0
    }
}"""


@pytest.fixture
def generic_ipv6_fast_advert_group_keepalived_config():
    return """
vrrp_instance vyatta-dp0p1s1-1 {
    state BACKUP
    interface dp0p1s1
    virtual_router_id 1
    version 3
    start_delay 0
    priority 100
    advert_int 0.5
    virtual_ipaddress {
        fe80::1/64
        2001::2/64
    }
    native_ipv6
    no_accept
}"""


@pytest.fixture
def second_dataplane_interface():
    return {
        "tagnode": "dp0p1s2",
        "vyatta-vrrp-v1:vrrp": {
            "start-delay": 0
        }
    }


@pytest.fixture
def switch_vif_interface():
    return {
        "name": "sw0",
        "vif": [
            {
                "tagnode": "10",
                "vyatta-vrrp-interfaces-switch-v1:vrrp": {
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
    return [
        {
            "tagnode": "sw0.10",
            "vyatta-vrrp-v1:vrrp": {
                "start-delay": 0,
                "vrrp-group": [copy.deepcopy(generic_group)]
            }
        }
    ]


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
def switch_vrrp_yang_name():
    return "vyatta-vrrp-interfaces-switch-v1:vrrp"


@pytest.fixture
def pathmon_yang_name():
    return (
        "vyatta-vrrp-path-monitor-track-interfaces-dataplane-v1:"
        "path-monitor"
    )


@pytest.fixture
def route_to_yang_name():
    return (
        "vyatta-vrrp-route-to-track-interfaces-dataplane-v1"
        ":route-to"
    )


@pytest.fixture
def bonding_pathmon_yang_name():
    return (
        "vyatta-vrrp-path-monitor-track-interfaces-bonding-v1:"
        "path-monitor"
    )


@pytest.fixture
def bonding_route_to_yang_name():
    return (
        "vyatta-vrrp-route-to-track-interfaces-bonding-v1"
        ":route-to"
    )


@pytest.fixture
def switch_pathmon_yang_name():
    return (
        "vyatta-vrrp-path-monitor-track-interfaces-switch-v1:"
        "path-monitor"
    )


@pytest.fixture
def switch_route_to_yang_name():
    return (
        "vyatta-vrrp-route-to-track-interfaces-switch-v1"
        ":route-to"
    )


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
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = [instance_state]
    return simple_yang_state


@pytest.fixture
def simple_rfc_state(simple_config, instance_state_rfc, vrrp_yang_name,
                     interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = [instance_state_rfc]
    return simple_yang_state


@pytest.fixture
def simple_rfc_sync_state(simple_config, instance_state_rfc_sync,
                          vrrp_yang_name, interface_yang_name,
                          dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = [instance_state_rfc_sync]
    return simple_yang_state


@pytest.fixture
def simple_rfc_ipao_state(simple_config, instance_state_rfc_ipao,
                          vrrp_yang_name, interface_yang_name,
                          dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = [instance_state_rfc_ipao]
    return simple_yang_state


@pytest.fixture
def simple_vif_state(simple_config, instance_state,
                     vrrp_yang_name, interface_yang_name,
                     vif_dataplane_list,
                     dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    simple_yang_state[interface_yang_name][dataplane_yang_name][0]["vif"] = \
        vif_dataplane_list
    vif_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name][0]["vif"]
    vif_list[0][vrrp_yang_name]["vrrp-group"] = \
        [instance_state]
    del vif_list[0][vrrp_yang_name]["start-delay"]
    return simple_yang_state


@pytest.fixture
def detailed_simple_state(simple_config, detailed_simple_keepalived_state,
                          vrrp_yang_name, interface_yang_name,
                          dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
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
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_rfc_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_simple_rfc_sync_state(simple_config,
                                   detailed_rfc_sync_simple_keepalived_state,
                                   vrrp_yang_name, interface_yang_name,
                                   dataplane_yang_name,
                                   sync_group_simple_keepalived_state):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_rfc_sync_simple_keepalived_state]
    simple_yang_state[vrrp_yang_name] = sync_group_simple_keepalived_state
    return simple_yang_state


@pytest.fixture
def detailed_simple_rfc_ipao_state(simple_config,
                                   detailed_rfc_ipao_simple_keepalived_state,
                                   vrrp_yang_name, interface_yang_name,
                                   dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
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
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
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
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_backup_track_intf_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_backup_track_intf_down_simple_state(
        simple_config, detailed_backup_track_intf_down_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_backup_track_intf_down_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_backup_track_intf_no_weight_simple_state(
        simple_config,
        detailed_backup_track_intf_no_weight_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
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
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_backup_track_pathmon_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_backup_track_multiple_pathmon_simple_state(
        simple_config,
        detailed_backup_multiple_track_pathmon_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_backup_multiple_track_pathmon_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_backup_track_route_simple_state(
        simple_config, detailed_backup_track_route_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_backup_track_route_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_track_multiple_simple_state(
        simple_config, detailed_track_multiple_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_track_multiple_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_v3_simple_state(simple_config,
                             detailed_v3_simple_keepalived_state,
                             vrrp_yang_name, interface_yang_name,
                             dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_v3_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_v3_rfc_fast_advert_simple_state(
        simple_config,
        detailed_v3_rfc_fast_advert_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name,
        dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_v3_rfc_fast_advert_simple_keepalived_state]
    return simple_yang_state


@pytest.fixture
def detailed_start_delay_simple_state(
        simple_config, detailed_start_delay_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name,
        dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
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
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
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
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    del dataplane_list[1][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_multi_group_first_simple_keepalived_state]
    dataplane_list[1][vrrp_yang_name]["vrrp-group"] = \
        [detailed_multi_group_second_simple_keepalived_state]
    simple_yang_state[vrrp_yang_name] = sync_group_simple_keepalived_state
    return simple_yang_state


@pytest.fixture
def detailed_vif_simple_state(simple_config,
                              detailed_simple_vif_keepalived_state,
                              vrrp_yang_name, interface_yang_name,
                              vif_dataplane_list,
                              dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]
    dataplane_list[0]["vif"] = \
        vif_dataplane_list
    vif_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name][0]["vif"]
    vif_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_simple_vif_keepalived_state]
    del vif_list[0][vrrp_yang_name]["start-delay"]
    return simple_yang_state


@pytest.fixture
def detailed_vif_simple_state_multiple_intf(
        simple_config, detailed_simple_vif_keepalived_state,
        detailed_simple_keepalived_state,
        vrrp_yang_name, interface_yang_name,
        vif_dataplane_list, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_simple_keepalived_state]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0]["vif"] = \
        vif_dataplane_list
    vif_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name][0]["vif"]
    vif_list[0][vrrp_yang_name]["vrrp-group"] = \
        [detailed_simple_vif_keepalived_state]
    del vif_list[0][vrrp_yang_name]["start-delay"]
    return simple_yang_state


@pytest.fixture
def simple_sync_group_state(
        simple_config, vrrp_yang_name, interface_yang_name,
        sync_group_simple_keepalived_state):
    simple_yang_state = copy.deepcopy(simple_config)
    del simple_yang_state[interface_yang_name]
    simple_yang_state[vrrp_yang_name] = sync_group_simple_keepalived_state
    return simple_yang_state


@pytest.fixture
def multiple_simple_sync_group_state(
        simple_config, vrrp_yang_name, interface_yang_name,
        multiple_sync_group_simple_keepalived_state):
    simple_yang_state = copy.deepcopy(simple_config)
    del simple_yang_state[interface_yang_name]
    simple_yang_state[vrrp_yang_name] = \
        multiple_sync_group_simple_keepalived_state
    return simple_yang_state


@pytest.fixture
def simple_vif_sync_group_state(
        simple_config, vrrp_yang_name, interface_yang_name,
        sync_group_simple_vif_keepalived_state):
    simple_yang_state = copy.deepcopy(simple_config)
    del simple_yang_state[interface_yang_name]
    simple_yang_state[vrrp_yang_name] = sync_group_simple_vif_keepalived_state
    return simple_yang_state


@pytest.fixture
def generic_group_complete_stats_dict(
        simple_config, generic_group_keepalived_stats_dict, vrrp_yang_name,
        interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [generic_group_keepalived_stats_dict]
    return simple_yang_state


@pytest.fixture
def backup_group_complete_stats_dict(
        simple_config, backup_group_keepalived_stats_dict, vrrp_yang_name,
        interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [backup_group_keepalived_stats_dict]
    return simple_yang_state


@pytest.fixture
def intf_complete_stats_dict(
        simple_config, generic_group_keepalived_stats_dict,
        backup_group_keepalived_stats_dict,
        vrrp_yang_name, interface_yang_name, dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [generic_group_keepalived_stats_dict,
            backup_group_keepalived_stats_dict]
    return simple_yang_state


@pytest.fixture
def multi_intf_complete_stats_dict(
        simple_config, generic_group_keepalived_stats_dict,
        backup_group_keepalived_stats_dict,
        second_intf_keepalived_stats_dict,
        vrrp_yang_name, interface_yang_name, second_dataplane_interface,
        dataplane_yang_name):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    dataplane_list.append(second_dataplane_interface)
    del dataplane_list[0][vrrp_yang_name]["start-delay"]
    del dataplane_list[1][vrrp_yang_name]["start-delay"]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [generic_group_keepalived_stats_dict,
            backup_group_keepalived_stats_dict]
    dataplane_list[1][vrrp_yang_name]["vrrp-group"] = \
        [second_intf_keepalived_stats_dict]
    return simple_yang_state


@pytest.fixture
def generic_group_vif_complete_stats_dict(
        simple_config, generic_group_vif_keepalived_stats_dict, vrrp_yang_name,
        interface_yang_name, dataplane_yang_name, vif_dataplane_list):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    del dataplane_list[0][vrrp_yang_name]
    dataplane_list[0]["vif"] = vif_dataplane_list
    vif_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name][0]["vif"]
    vif_list[0][vrrp_yang_name]["vrrp-group"] = \
        [generic_group_vif_keepalived_stats_dict]
    del vif_list[0][vrrp_yang_name]["start-delay"]
    return simple_yang_state


@pytest.fixture
def generic_group_vif_and_parent_complete_stats_dict(
        simple_config, generic_group_vif_keepalived_stats_dict,
        generic_group_keepalived_stats_dict, vrrp_yang_name,
        interface_yang_name, dataplane_yang_name, vif_dataplane_list):
    simple_yang_state = copy.deepcopy(simple_config)
    dataplane_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name]
    dataplane_list[0][vrrp_yang_name]["vrrp-group"] = \
        [generic_group_keepalived_stats_dict]
    dataplane_list[0]["vif"] = vif_dataplane_list
    vif_list = \
        simple_yang_state[interface_yang_name][dataplane_yang_name][0]["vif"]
    vif_list[0][vrrp_yang_name]["vrrp-group"] = \
        [generic_group_vif_keepalived_stats_dict]
    del vif_list[0][vrrp_yang_name]["start-delay"]
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
def generic_v3_fast_advert_config(
        top_level_dictionary, interface_yang_name,
        dataplane_yang_name, dataplane_list,
        dataplane_interface, generic_v3_fast_advert_group,
        vrrp_yang_name):
    dataplane_interface[vrrp_yang_name]["vrrp-group"] = \
        [generic_v3_fast_advert_group]
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
def bonding_config(top_level_dictionary, interface_yang_name,
                   bonding_yang_name, bonding_list, vrrp_yang_name):
    simple_yang_config = copy.deepcopy(top_level_dictionary)
    simple_yang_config[interface_yang_name][bonding_yang_name] = \
        copy.deepcopy(bonding_list)
    intf_list = simple_yang_config[interface_yang_name]
    bonding_intf = intf_list[bonding_yang_name][0][vrrp_yang_name]
    bonding_intf["start-delay"] = 60
    bonding_intf["vrrp-group"][0]["virtual-address"] = \
        ["10.11.2.100/25"]
    bonding_intf["vrrp-group"][0]["tagnode"] = 2
    del bonding_intf["vrrp-group"][0]["priority"]
    return simple_yang_config


@pytest.fixture
def bonding_complex_config(
    top_level_dictionary, interface_yang_name, bonding_yang_name,
    bonding_interface, bonding_max_config_group, vrrp_yang_name
):
    new_interface = copy.deepcopy(bonding_interface)
    new_interface[vrrp_yang_name]["vrrp-group"] = \
        [copy.deepcopy(bonding_max_config_group)]
    complex_yang_config = copy.deepcopy(top_level_dictionary)
    complex_yang_config[interface_yang_name][bonding_yang_name] =\
        [new_interface]
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
    simple_yang_config = copy.deepcopy(top_level_dictionary)
    simple_yang_config[interface_yang_name][dataplane_yang_name] = \
        copy.deepcopy(dataplane_list)
    simple_yang_config[interface_yang_name][dataplane_yang_name][0]["vif"] = \
        copy.deepcopy(vif_dataplane_list)
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
def switch_complex_config(
        top_level_dictionary, interface_yang_name, switch_yang_name,
        switch_list, switch_max_config_group, vrrp_yang_name,
        switch_vrrp_yang_name):
    switch_list_copy = copy.deepcopy(switch_list)
    new_interface = switch_list_copy[0]
    del new_interface[vrrp_yang_name]
    vif_interface = new_interface["vif"][0]
    vif_interface[switch_vrrp_yang_name]["vrrp-group"] = \
        [copy.deepcopy(switch_max_config_group)]
    complex_yang_config = copy.deepcopy(top_level_dictionary)
    complex_yang_config[interface_yang_name][switch_yang_name] =\
        switch_list_copy
    return complex_yang_config


@pytest.fixture
def syncgroup_config(top_level_dictionary, interface_yang_name,
                     dataplane_yang_name, syncgroup_dataplane_list):
    syncgroup_yang_config = top_level_dictionary
    syncgroup_yang_config[interface_yang_name][dataplane_yang_name] =\
        syncgroup_dataplane_list
    return syncgroup_yang_config


@pytest.fixture
def multiple_syncgroup_config(
    top_level_dictionary, interface_yang_name, dataplane_yang_name,
    multiple_syncgroup_dataplane_list
):
    syncgroup_yang_config = top_level_dictionary
    syncgroup_yang_config[interface_yang_name][dataplane_yang_name] =\
        multiple_syncgroup_dataplane_list
    return syncgroup_yang_config


@pytest.fixture
def no_vrrp_config(
        top_level_dictionary, interface_yang_name, dataplane_yang_name,
        dataplane_list, vrrp_yang_name):
    simple_yang_config = copy.deepcopy(top_level_dictionary)
    new_list = copy.deepcopy(dataplane_list)
    simple_yang_config[interface_yang_name][dataplane_yang_name] = \
        new_list
    del new_list[0][vrrp_yang_name]["vrrp-group"]
    return simple_yang_config


@pytest.fixture
def simple_multi_intf_same_type_config(
        top_level_dictionary, interface_yang_name,
        dataplane_yang_name, dataplane_list,
        second_dataplane_interface):
    simple_yang_config = copy.deepcopy(top_level_dictionary)
    simple_yang_config[interface_yang_name][dataplane_yang_name] =\
        copy.deepcopy(dataplane_list)
    simple_yang_config[interface_yang_name][dataplane_yang_name].append(
        second_dataplane_interface)
    return simple_yang_config


@pytest.fixture
def simple_multi_intf_differing_type_config(
        top_level_dictionary, interface_yang_name,
        dataplane_yang_name, bonding_yang_name,
        dataplane_list, second_dataplane_interface,
        bonding_list):
    simple_yang_config = copy.deepcopy(top_level_dictionary)
    simple_yang_config[interface_yang_name][dataplane_yang_name] =\
        copy.deepcopy(dataplane_list)
    simple_yang_config[interface_yang_name][dataplane_yang_name].append(
        second_dataplane_interface)
    simple_yang_config[interface_yang_name][bonding_yang_name] = \
        bonding_list
    return simple_yang_config


@pytest.fixture
def simple_multi_intf_differing_type_config_sanitized(
        top_level_dictionary, interface_yang_name,
        dataplane_yang_name, bonding_yang_name,
        dataplane_list, bonding_list):
    simple_yang_config = copy.deepcopy(top_level_dictionary)
    simple_yang_config[interface_yang_name][dataplane_yang_name] =\
        copy.deepcopy(dataplane_list)
    simple_yang_config[interface_yang_name][bonding_yang_name] = \
        bonding_list
    return simple_yang_config


@pytest.fixture
def simple_dataplane_vif_with_vrrp_config(
        top_level_dictionary, interface_yang_name, dataplane_yang_name,
        vrrp_yang_name,
        vif_dataplane_interface, dataplane_list, generic_group):
    simple_yang_config = copy.deepcopy(top_level_dictionary)
    simple_yang_config[interface_yang_name][dataplane_yang_name] = \
        copy.deepcopy(dataplane_list)
    simple_yang_config[interface_yang_name][dataplane_yang_name][0]["vif"] = \
        [copy.deepcopy(vif_dataplane_interface)]
    vif_list = \
        simple_yang_config[interface_yang_name][dataplane_yang_name][0]["vif"]
    vif_list[0][vrrp_yang_name]["vrrp-group"] = \
        [copy.deepcopy(generic_group)]
    return simple_yang_config


@pytest.fixture
def simple_dataplane_vif_sanitized_config(
        top_level_dictionary, interface_yang_name, dataplane_yang_name,
        vif_dataplane_list_sanitized, dataplane_list):
    simple_yang_config = copy.deepcopy(top_level_dictionary)
    simple_yang_config[interface_yang_name]["vif"] = \
        copy.deepcopy(vif_dataplane_list_sanitized)
    simple_yang_config[interface_yang_name][dataplane_yang_name] = \
        copy.deepcopy(dataplane_list)
    return simple_yang_config


@pytest.fixture
def simple_multi_intf_type_vif_config(
        top_level_dictionary, interface_yang_name, dataplane_yang_name,
        bonding_yang_name, vrrp_yang_name,
        vif_dataplane_list, dataplane_list,
        vif_bonding_list, bonding_list, generic_group):
    simple_yang_config = copy.deepcopy(top_level_dictionary)
    simple_yang_config[interface_yang_name][dataplane_yang_name] = \
        copy.deepcopy(dataplane_list)
    simple_yang_config[interface_yang_name][dataplane_yang_name][0]["vif"] = \
        copy.deepcopy(vif_dataplane_list)
    dp_vif = \
        simple_yang_config[interface_yang_name][dataplane_yang_name][0]["vif"]
    dp_vif[0][vrrp_yang_name]["vrrp-group"] = [copy.deepcopy(generic_group)]
    simple_yang_config[interface_yang_name][bonding_yang_name] = \
        copy.deepcopy(bonding_list)
    simple_yang_config[interface_yang_name][bonding_yang_name][0]["vif"] = \
        copy.deepcopy(vif_bonding_list)
    bond_vif = \
        simple_yang_config[interface_yang_name][bonding_yang_name][0]["vif"]
    modified_group = copy.deepcopy(generic_group)
    modified_group["tagnode"] = 50
    bond_vif[0][vrrp_yang_name]["vrrp-group"] = [modified_group]
    return simple_yang_config


@pytest.fixture
def simple_multi_intf_type_vif_sanitized_config(
        top_level_dictionary, interface_yang_name, dataplane_yang_name,
        bonding_yang_name, dataplane_list, bonding_list,
        vif_two_type_list_sanitized):
    simple_yang_config = top_level_dictionary
    simple_yang_config[interface_yang_name][dataplane_yang_name] = \
        copy.deepcopy(dataplane_list)
    simple_yang_config[interface_yang_name][bonding_yang_name] = \
        copy.deepcopy(bonding_list)
    simple_yang_config[interface_yang_name]["vif"] = \
        copy.deepcopy(vif_two_type_list_sanitized)
    return simple_yang_config


@pytest.fixture
def parent_and_vif_config(
    simple_dataplane_vif_config, interface_yang_name,
    dataplane_yang_name, vrrp_yang_name, generic_group
):
    new_yang_config = copy.deepcopy(simple_dataplane_vif_config)
    intf_level = new_yang_config[interface_yang_name]
    vif_intf = intf_level[dataplane_yang_name][0]["vif"][0]
    vif_group = copy.deepcopy(generic_group)
    vif_group["virtual-address"] = ["10.10.2.100/25"]
    del vif_group["priority"]
    vif_group["tagnode"] = 2
    vif_intf[vrrp_yang_name]["vrrp-group"] = [vif_group]
    return new_yang_config


@pytest.fixture
def switch_config(
    simple_switch_config, interface_yang_name,
    switch_yang_name, vrrp_yang_name, generic_rfc_group,
    switch_vrrp_yang_name
):
    new_yang_config = copy.deepcopy(simple_switch_config)
    intf_level = new_yang_config[interface_yang_name]
    vif_intf = intf_level[switch_yang_name][0]["vif"][0]
    del intf_level[switch_yang_name][0][vrrp_yang_name]
    del vif_intf[switch_vrrp_yang_name]
    vif_group = copy.deepcopy(generic_rfc_group)
    vif_intf[switch_vrrp_yang_name] = {
        "start-delay": 0,
        "vrrp-group": [vif_group]
    }
    return new_yang_config


@pytest.fixture
def disabled_vrrp_config(
    interface_yang_name, dataplane_yang_name, vrrp_yang_name,
    disabled_group, dataplane_interface
):
    disabled_interface = copy.deepcopy(dataplane_interface)
    disabled_interface["vyatta-vrrp-v1:vrrp"]["vrrp-group"] = [
        disabled_group
    ]
    disabled_config = {
        interface_yang_name: {
            dataplane_yang_name: [copy.deepcopy(disabled_interface)]
        }
    }
    return disabled_config


@pytest.fixture
def vif_dataplane_interface():
    return {
        "tagnode": "10",
        "vyatta-vrrp-v1:vrrp": {
            "start-delay": 0
        }
    }


@pytest.fixture
def vif_dataplane_list(vif_dataplane_interface):
    return [copy.deepcopy(vif_dataplane_interface)]


@pytest.fixture
def vif_dataplane_interface_sanitized(generic_group):
    return {
        "tagnode": "dp0p1s1.10",
        "vyatta-vrrp-v1:vrrp": {
            "start-delay": 0,
            "vrrp-group": [copy.deepcopy(generic_group)]
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
    return {
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
    modified_group = copy.deepcopy(generic_group)
    modified_group["tagnode"] = 50
    return {
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
    return {
        "tagnode": "dp0bond0",
        "vyatta-vrrp-v1:vrrp": {
            "start-delay": 0,
            "vrrp-group": [copy.deepcopy(generic_group)]
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
        dynamic_interfaces allow_if_changes
}"""


@pytest.fixture
def simple_keepalived_config(autogeneration_string,
                             dataplane_group_keepalived_config):
    return f"{autogeneration_string}{dataplane_group_keepalived_config}"


@pytest.fixture
def generic_v3_keepalived_config(
        autogeneration_string,
        generic_v3_group_keepalived_config):
    return (
        f"{autogeneration_string}"
        f"{generic_v3_group_keepalived_config}"
    )


@pytest.fixture
def simple_v3_keepalived_config(
        autogeneration_string,
        generic_ipv6_fast_advert_group_keepalived_config):
    return (
        f"{autogeneration_string}"
        f"{generic_ipv6_fast_advert_group_keepalived_config}"
    )


@pytest.fixture
def syncgroup_keepalived_config(
    autogeneration_string, syncgroup_keepalived_section,
    syncgroup1_keepalived_config, syncgroup2_keepalived_config,
):
    return (
        f"{autogeneration_string}"
        f"{syncgroup_keepalived_section}"
        f"{syncgroup1_keepalived_config}"
        f"{syncgroup2_keepalived_config}"
    )


@pytest.fixture
def multiple_syncgroup_keepalived_config(
    autogeneration_string, syncgroup_keepalived_section,
    second_syncgroup_keepalived_section,
    syncgroup1_keepalived_config, syncgroup2_keepalived_config,
    syncgroup3_keepalived_config, syncgroup4_keepalived_config
):
    return (
        f"{autogeneration_string}"
        f"{syncgroup_keepalived_section}"
        f"{second_syncgroup_keepalived_section}"
        f"{syncgroup1_keepalived_config}"
        f"{syncgroup2_keepalived_config}"
        f"{syncgroup3_keepalived_config}"
        f"{syncgroup4_keepalived_config}"
    )


@pytest.fixture
def multiple_group_keepalived_config(
        autogeneration_string,
        dataplane_group_keepalived_config,
        bonding_group_keepalived_config):
    return (
        f"{autogeneration_string}"
        f"{dataplane_group_keepalived_config}"
        f"{bonding_group_keepalived_config}"
    )


@pytest.fixture
def complex_keepalived_config(
        autogeneration_string,
        max_group_keepalived_config):
    return (
        f"{autogeneration_string}"
        f"{max_group_keepalived_config}"
    )


@pytest.fixture
def bonding_keepalived_config(
        autogeneration_string,
        bonding_group_keepalived_config):
    return (
        f"{autogeneration_string}"
        f"{bonding_group_keepalived_config}"
    )


@pytest.fixture
def bonding_complex_keepalived_config(
        autogeneration_string,
        bonding_max_group_keepalived_config):
    return (
        f"{autogeneration_string}"
        f"{bonding_max_group_keepalived_config}"
    )


@pytest.fixture
def parent_and_vif_keepalived_config(
        autogeneration_string,
        dataplane_group_keepalived_config,
        dataplane_vif_group_keepalived_config):
    return (
        f"{autogeneration_string}"
        f"{dataplane_group_keepalived_config}"
        f"{dataplane_vif_group_keepalived_config}"
    )


@pytest.fixture
def switch_keepalived_config(
        autogeneration_string,
        switch_rfc_group_keepalived_config):
    return (
        f"{autogeneration_string}"
        f"{switch_rfc_group_keepalived_config}"
    )


@pytest.fixture
def switch_complex_keepalived_config(
        autogeneration_string,
        switch_max_group_keepalived_config):
    return (
        f"{autogeneration_string}"
        f"{switch_max_group_keepalived_config}"
    )


@pytest.fixture
def vif_complex_keepalived_config(
        autogeneration_string,
        vif_max_group_keepalived_config):
    return (
        f"{autogeneration_string}"
        f"{vif_max_group_keepalived_config}"
    )


@pytest.fixture
def autogeneration_config_block(autogeneration_string):
    return [
        [line.strip(" ") for line in autogeneration_string.splitlines()[6:]]
    ]


@pytest.fixture
def simple_keepalived_config_block(
        dataplane_group_keepalived_config):
    return [
        [
            line.strip(" ")
            for line in dataplane_group_keepalived_config.splitlines()[1:]
        ]
    ]


@pytest.fixture
def multiple_group_keepalived_config_block(
        dataplane_group_keepalived_config,
        bonding_group_keepalived_config):
    return [
        [
            line.strip(" ")
            for line in dataplane_group_keepalived_config.splitlines()[1:]
        ],
        [
            line.strip(" ")
            for line in bonding_group_keepalived_config.splitlines()[1:]
        ]
    ]


@pytest.fixture
def complex_keepalived_config_block(max_group_keepalived_config):
    return [
        [
            line.strip(" ")
            for line in max_group_keepalived_config.splitlines()[1:]
        ]
    ]


@pytest.fixture
def pathmon_track_group_keepalived_config_block(
        pathmon_track_group_keepalived_config):
    return [
        [
            line.strip(" ")
            for line in pathmon_track_group_keepalived_config.splitlines()[1:]
        ]
    ]


@pytest.fixture
def route_to_track_group_keepalived_config_block(
        route_to_track_group_keepalived_config):
    return [
        [
            line.strip(" ")
            for line in route_to_track_group_keepalived_config.splitlines()[1:]
        ]
    ]


@pytest.fixture
def switch_rfc_group_keepalived_config_block(
        switch_rfc_group_keepalived_config):
    return [
        [
            line.strip(" ")
            for line in switch_rfc_group_keepalived_config.splitlines()[1:]
        ]
    ]


@pytest.fixture
def dataplane_vif_group_keepalived_config_block(
        dataplane_vif_group_keepalived_config):
    return [
        [
            line.strip(" ")
            for line in dataplane_vif_group_keepalived_config.splitlines()[1:]
        ]
    ]


@pytest.fixture
def syncgroup_group_keepalived_config_block(
        syncgroup_keepalived_config):
    block = [
        [
            line.strip(" ")
            for line in syncgroup_keepalived_config.splitlines()[1:]
        ]
    ]
    block[0].append("sync_group TEST")
    return block


@pytest.fixture
def v3_fast_advert_group_keepalived_config_block(
        generic_v3_fast_advert_group_keepalived_config):
    block = [
        [
            line.strip(" ")
            for line in
            generic_v3_fast_advert_group_keepalived_config.splitlines()[1:]
        ]
    ]
    return block


@pytest.fixture
def v3_fast_advert_group_seconds_keepalived_config_block(
        generic_v3_fast_advert_group_seconds_keepalived_config):
    block = [
        [
            line.strip(" ")
            for line in
            generic_v3_fast_advert_group_seconds_keepalived_config.splitlines(
            )[1:]
        ]
    ]
    return block


@pytest.fixture
def v3_fast_advert_group_between_seconds_keepalived_config_block(
        generic_v3_fast_advert_group_between_seconds_keepalived_config):
    pep8_workaround = \
        generic_v3_fast_advert_group_between_seconds_keepalived_config
    block = [
        [
            line.strip(" ")
            for line in
            pep8_workaround.splitlines()[1:]
        ]
    ]
    return block


@pytest.fixture
def complete_state_yang(top_level_dictionary, interface_yang_name,
                        dataplane_yang_name, generic_group_state,
                        vrrp_yang_name):
    state_config = top_level_dictionary
    intf = {
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
def complete_state_vif_yang(
        top_level_dictionary, interface_yang_name,
        dataplane_yang_name, generic_group_state,
        vrrp_yang_name):
    state_config = top_level_dictionary
    intf = {
        "tagnode": "dp0p1s1",
        "vif": [
            {
                "tagnode": "10",
                vrrp_yang_name:
                    {
                        "vrrp-group":
                        [
                            {"instance-state": generic_group_state,
                             "tagnode": "2"}
                        ]
                    }
            }
        ]
    }
    state_config[interface_yang_name][dataplane_yang_name] =\
        [intf]
    return state_config


@pytest.fixture
def mock_show_version_rpc_kvm():
    import vyatta

    class MockConfigd:

        class Client:

            def __init__(self):
                pass

            def call_rpc_dict(self, source, action, arguments):
                return {"output": "Hypervisor: KVM"}

    setattr(vyatta, "configd", MockConfigd)


@pytest.fixture
def mock_show_version_rpc_vmware():
    import vyatta

    class MockConfigd:

        class Client:

            def __init__(self):
                pass

            def call_rpc_dict(self, source, action, arguments):
                return {"output": "Hypervisor: VMware"}

    setattr(vyatta, "configd", MockConfigd)


@pytest.fixture
def mock_show_version_rpc_no_hypervisor():
    import vyatta

    class MockConfigd:

        class Client:

            def __init__(self):
                pass

            def call_rpc_dict(self, source, action, arguments):
                return {"output": ""}

    setattr(vyatta, "configd", MockConfigd)


@pytest.fixture
def mock_pydbus(pydbus_fakes, tmp_path):
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
            return ("/org/freedesktop/systemd1/"
                    "unit/vyatta_keepalived_service")

    class PropertyInterface:

        def __init__(self):
            pass

        def GetAll(self, interface_name):  # noqa: N802
            if interface_name == "dp0p1s1":
                return {"Name": ("vyatta-dp0p1s1-1",),
                        "SyncGroup": ("",),
                        "XmitIntf": ("dp0p1s1",),
                        "State": (2, "Master"),
                        "LastTransition": (0,),
                        "AddressOwner": (False,)
                        }
            if interface_name == "dp0p1s1.10":
                return {"Name": ("vyatta-dp0p1s1.10-1",),
                        "SyncGroup": ("",),
                        "XmitIntf": ("dp0p1s1.10",),
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

        def PrintData(self):
            with open(f"{tmp_path}/keepalived.data", "w") as file_obj:
                file_obj.write("test")
            return

        def PrintStats(self):
            with open(f"{tmp_path}/keepalived.stats", "w") as file_obj:
                file_obj.write("test")
            return

        def __getitem__(self, name):
            return PropertyInterface()

    class MockSystemBus:

        def get(self, obj_name, obj_path):

            if "/org/freedesktop/systemd1/unit/" + \
                    "vyatta_keepalived_service" == obj_path or \
                    obj_name in ("org.keepalived.Vrrp1",
                                 "org.keepalived.Vrrp1.Instance"):
                return VrrpProxyObject()
            if "/org/freedesktop/systemd1" == obj_path:
                return SystemdProxyObject()

        def watch_name(self, name, name_appeared=None):
            return

    setattr(pydbus, "SystemBus", MockSystemBus)
    return PropertyInterface


@pytest.fixture
def mock_pydbus_rfc(mock_pydbus):
    def GetAllRfc(self, interface_name):  # noqa: N802
        return {"Name": ("vyatta-dp0p1s1-1",),
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
    with open(f"{tmp_path}/snmpd.conf", "w") as fh:
        fh.write(config_string)


# find interface in yang fixtures


@pytest.fixture
def search_empty_dataplane_list(
        interface_yang_name, dataplane_yang_name, simple_config,
        dataplane_interface, vrrp_yang_name):
    new_yang = copy.deepcopy(simple_config)
    new_yang[interface_yang_name][dataplane_yang_name] = []
    interface_list = new_yang[interface_yang_name][dataplane_yang_name]
    return interface_list


@pytest.fixture
def search_dataplane_list(
        interface_yang_name, dataplane_yang_name, simple_config,):
    new_yang = copy.deepcopy(simple_config)
    interface_list = new_yang[interface_yang_name][dataplane_yang_name]
    return interface_list


@pytest.fixture
def search_vif_dataplane_list(
    interface_yang_name, dataplane_yang_name, simple_config,
    vif_dataplane_interface
):
    new_yang = copy.deepcopy(simple_config)
    interface_list = new_yang[interface_yang_name][dataplane_yang_name]
    interface_list[0]["vif"] = [copy.deepcopy(vif_dataplane_interface)]
    return interface_list


@pytest.fixture
def search_vif_dataplane_list_multiple_vrrp_groups(
    interface_yang_name, dataplane_yang_name, simple_config,
    vif_dataplane_interface, generic_group
):
    new_yang = copy.deepcopy(simple_config)
    interface_list = new_yang[interface_yang_name][dataplane_yang_name]
    multi_vif_groups = copy.deepcopy(vif_dataplane_interface)
    multi_vif_groups["vrrp-group"] = copy.deepcopy(generic_group)
    interface_list[0]["vif"] = [multi_vif_groups]
    return interface_list


# Data from running instances


@pytest.fixture
def switch_config_not_being_applied():
    return {
        "vyatta-interfaces-v1:interfaces": {
            "vyatta-interfaces-dataplane-v1:dataplane": [
                {
                    "tagnode": "dp0p1s0",
                    "vyatta-vrrp-v1:vrrp": {
                        "start-delay": 0
                    }
                },
                {
                    "tagnode": "dp0xe1",
                    "vyatta-vrrp-v1:vrrp": {
                        "start-delay": 0
                    }
                },
                {
                    "tagnode": "dp0xe2",
                    "vyatta-vrrp-v1:vrrp": {
                        "start-delay": 0
                    }
                },
                {
                    "tagnode": "dp0xe4",
                    "vyatta-vrrp-v1:vrrp": {
                        "start-delay": 0
                    }
                }
            ],
            "vyatta-interfaces-switch-v1:switch": [
                {
                    "name": "sw0",
                    "vif": [
                        {
                            "tagnode": "10",
                            "vyatta-vrrp-interfaces-switch-v1:vrrp": {
                                "start-delay": 0,
                                "vrrp-group": [
                                    {
                                        "accept": False,
                                        "preempt": True,
                                        "priority": 22,
                                        "rfc-compatibility": [
                                            None
                                        ],
                                        "tagnode": 10,
                                        "version": 3,
                                        "virtual-address": [
                                            "11.0.0.254"
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
    }


@pytest.fixture
def expected_switch_config_not_being_applied():
    return {
        "vyatta-interfaces-v1:interfaces": {
            "vif": [
                {
                    "tagnode": "sw0.10",
                    "vyatta-vrrp-v1:vrrp": {
                        "start-delay": 0,
                        "vrrp-group": [
                            {
                                "accept": False,
                                "preempt": True,
                                "priority": 22,
                                "rfc-compatibility": [
                                    None
                                ],
                                "tagnode": 10,
                                "version": 3,
                                "virtual-address": [
                                    "11.0.0.254"
                                ]
                            }
                        ]
                    }
                }
            ]
        }
    }


@pytest.fixture
def switch_show_dictionary():
    return {
        'vyatta-interfaces-v1:interfaces': {
            'vyatta-interfaces-switch-v1:switch': [
                {
                    'name': 'sw0',
                    'vif': [
                        {
                            'tagnode': '10',
                            'vyatta-vrrp-v1:vrrp': {
                                'vrrp-group': [
                                    {
                                        'instance-state': {
                                            'address-owner': False,
                                            'last-transition': 0,
                                            'rfc-interface': 'sw0vrrp1',
                                            'state': 'MASTER',
                                            'sync-group': ''
                                        },
                                        'tagnode': '10'
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
    }


@pytest.fixture
def switch_show_vrrp_output():
    return """
                                 RFC        Addr   Last        Sync
Interface         Group  State   Compliant  Owner  Transition  Group
---------         -----  -----   ---------  -----  ----------  -----
sw0.10            10     MASTER  sw0vrrp1   no     3s          <none>

"""
