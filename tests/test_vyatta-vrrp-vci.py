#! /usr/bin/python3

# Copyright (c) 2019,2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import json
from pathlib import Path
import pytest

import vyatta.keepalived.util as util


class TestVyattaVrrpVci:

    # pylint: disable=protected-access
    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=too-many-arguments

    @pytest.mark.sanity
    def test_vci_config_get(self, mock_pydbus,
                            test_config, simple_config,
                            tmp_file_keepalived_config):
        result = json.dumps(simple_config)
        test_config._conf_obj = tmp_file_keepalived_config
        expect = test_config.get()
        assert result == expect

    @pytest.mark.sanity
    def test_vci_state_get(self, complete_state_yang,
                           mock_pydbus, test_state,
                           tmp_file_keepalived_config):
        expected = complete_state_yang
        test_state._conf_obj = tmp_file_keepalived_config
        test_state.pc.keepalived_proxy_obj.SubState = "running"
        util.VRRP_INSTANCE_DBUS_INTF_NAME = "dp0p1s1"
        result = test_state.get()
        assert expected == result

    @pytest.mark.sanity
    def test_vci_state_get_with_vif(
            self, complete_state_vif_yang,
            mock_pydbus, test_state_vif,
            tmp_file_keepalived_vif_config):
        expected = complete_state_vif_yang
        test_state_vif._conf_obj = tmp_file_keepalived_vif_config
        test_state_vif.pc.keepalived_proxy_obj.SubState = "running"
        util.VRRP_INSTANCE_DBUS_INTF_NAME = "dp0p1s1.10"
        result = test_state_vif.get()
        assert expected == result

    @pytest.mark.sanity
    def test_vci_state_get_not_running(
            self, mock_pydbus, test_state,
            tmp_file_keepalived_config):
        expected = {}
        test_state._conf_obj = tmp_file_keepalived_config
        result = test_state.get()
        assert expected == result

    @pytest.mark.sanity
    def test_vci_config_get_with_syncgroup(
            self, mock_pydbus, test_config, syncgroup_config,
            tmp_file_syncgroup_keepalived_config):
        result = json.dumps(syncgroup_config)
        test_config._conf_obj = tmp_file_syncgroup_keepalived_config
        expect = test_config.get()
        assert result == expect

    @pytest.mark.sanity
    def test_vci_config_set_no_config(
            self, mock_pydbus, test_config,
            top_level_dictionary):
        result = False
        test_config.set(top_level_dictionary)
        conf_path = Path(
            test_config._conf_obj.config_file_path())
        expected = conf_path.exists()
        assert result == expected

    @pytest.mark.sanity
    def test_vci_config_set_writes_file(
            self, mock_pydbus, test_config,
            simple_config):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        pc.keepalived_proxy_obj.SubState = "running"
        result = True
        test_config.set(simple_config)
        conf_path = Path(
            test_config._conf_obj.config_file_path())
        expected = conf_path.exists()
        assert result == expected

    @pytest.mark.sanity
    def test_vci_config_set_writes_correct_config(
            self, mock_pydbus, test_config,
            simple_config, simple_keepalived_config):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        pc.keepalived_proxy_obj.SubState = "running"
        result = True
        file_path = \
            test_config._conf_obj.config_file_path()
        test_config.set(simple_config)
        conf_path = Path(
            test_config._conf_obj.config_file_path())
        expected = conf_path.exists()
        assert result == expected
        file_contents = ""
        with open(file_path, "r") as file_handle:
            file_contents = file_handle.read()
        assert file_contents == simple_keepalived_config

    @pytest.mark.sanity
    def test_vci_config_set_writes_correct_syncgroup_config(
            self, mock_pydbus, test_config,
            syncgroup_config, syncgroup_keepalived_config):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        pc.keepalived_proxy_obj.SubState = "running"
        result = True
        file_path = \
            test_config._conf_obj.config_file_path()
        test_config.set(syncgroup_config)
        conf_path = Path(
            test_config._conf_obj.config_file_path())
        expected = conf_path.exists()
        assert result == expected
        file_contents = ""
        with open(file_path, "r") as file_handle:
            file_contents = file_handle.read()
        assert file_contents == syncgroup_keepalived_config

    @pytest.mark.sanity
    def test_vci_config_check_local_address(
            self, mock_pydbus, test_config, simple_config,
            interface_yang_name,
            dataplane_yang_name, vrrp_yang_name):
        intf = simple_config[interface_yang_name][dataplane_yang_name][0]
        intf[vrrp_yang_name]["vrrp-group"][0]["hello-source-address"] =\
            "127.0.0.1"
        result = None
        expect = test_config.check(simple_config)
        assert result == expect

    @pytest.mark.sanity
    def test_vci_config_check_non_local_address(
            self, mock_pydbus, test_config, simple_config,
            interface_yang_name,
            dataplane_yang_name, vrrp_yang_name):
        intf = simple_config[interface_yang_name][dataplane_yang_name][0]
        intf[vrrp_yang_name]["vrrp-group"][0]["hello-source-address"] =\
            "10.0.0.1"
        with pytest.raises(OSError):
            test_config.check(simple_config)

    @pytest.mark.sanity
    def test_vci_config_set_cleans_up_file(
            self, mock_pydbus, test_config,
            simple_config, top_level_dictionary):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        pc.keepalived_proxy_obj.SubState = "running"
        result = True
        test_config.set(simple_config)
        conf_path = Path(
            test_config._conf_obj.config_file_path())
        expected = conf_path.exists()
        assert result == expected
        test_config.pc.keepalived_proxy_obj.SubState = "running"
        result = False
        test_config.set(top_level_dictionary)
        conf_path = Path(
            test_config._conf_obj.config_file_path())
        expected = conf_path.exists()
        assert result == expected

    def test_vci_config_check_simple_config(
            self, mock_pydbus, test_config, simple_config):
        result = None
        expect = test_config.check(simple_config)
        assert result == expect

    def test_vci_config_check_fuller_config(
            self, mock_pydbus, test_config, complex_config,
            mock_show_version_rpc_no_hypervisor):
        result = None
        expect = test_config.check(complex_config)
        assert result == expect

    @pytest.mark.sanity
    def test_vci_config_check_fuller_config_printed_warnings(
            self, mock_pydbus, test_config, complex_config,
            mock_show_version_rpc_vmware, capsys):
        result = None
        print_result = "RFC compatibility is not supported on VMware\n\n"
        expect = test_config.check(complex_config)
        captured = capsys.readouterr()
        assert result == expect
        assert print_result == captured.out

    @pytest.mark.sanity
    def test_vci_config_set_writes_disabled_group(
            self, mock_pydbus, test_config, interface_yang_name,
            autogeneration_string,
            dataplane_yang_name, disabled_group,
            dataplane_interface):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        pc.keepalived_proxy_obj.SubState = "running"
        file_path = \
            test_config._conf_obj.config_file_path()
        disabled_interface = dataplane_interface
        disabled_interface["vyatta-vrrp-v1:vrrp"]["vrrp-group"] = [
            disabled_group
        ]
        disabled_config = {
            interface_yang_name: {
                dataplane_yang_name: [disabled_interface]
            }
        }
        test_config.set(disabled_config)
        conf_path = Path(
            test_config._conf_obj.config_file_path())
        expected = conf_path.exists()
        result = True
        assert result == expected
        file_contents = ""
        with open(file_path, "r") as file_handle:
            file_contents = file_handle.read()
        assert file_contents == autogeneration_string

    def test_vci_config_set_writes_correct_v3_config(
            self, mock_pydbus, test_config,
            generic_v3_fast_advert_config,
            simple_v3_keepalived_config):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        pc.keepalived_proxy_obj.SubState = "running"
        result = True
        file_path = \
            test_config._conf_obj.config_file_path()
        test_config.set(generic_v3_fast_advert_config)
        conf_path = Path(
            test_config._conf_obj.config_file_path())
        expected = conf_path.exists()
        assert result == expected
        file_contents = ""
        with open(file_path, "r") as file_handle:
            file_contents = file_handle.read()
        assert file_contents == simple_v3_keepalived_config
