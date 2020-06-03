#! /usr/bin/python3

# Copyright (c) 2019,2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

import json
import logging
from pathlib import Path

import pytest

import vyatta.vrrp_vci.keepalived.util as util


class TestVyattaVrrpVci:

    # pylint: disable=protected-access
    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=too-many-arguments

    @pytest.mark.sanity
    def test_vci_config_get(self, mock_pydbus,
                            test_config, simple_config,
                            tmp_file_keepalived_config):
        test_config._conf_obj = tmp_file_keepalived_config

        expected = json.dumps(simple_config)
        assert test_config.get() == expected

    @pytest.mark.sanity
    def test_vci_state_get(self, complete_state_yang,
                           mock_pydbus, test_state,
                           tmp_file_keepalived_config):
        test_state._conf_obj = tmp_file_keepalived_config
        test_state.pc.keepalived_proxy_obj.SubState = "running"
        util.VRRP_INSTANCE_DBUS_INTF_NAME = "dp0p1s1"

        expected = complete_state_yang
        assert test_state.get() == expected

    @pytest.mark.sanity
    def test_vci_state_get_with_vif(
            self, complete_state_vif_yang,
            mock_pydbus, test_state_vif,
            tmp_file_keepalived_vif_config):
        test_state_vif._conf_obj = tmp_file_keepalived_vif_config
        test_state_vif.pc.keepalived_proxy_obj.SubState = "running"
        util.VRRP_INSTANCE_DBUS_INTF_NAME = "dp0p1s1.10"

        expected = complete_state_vif_yang
        assert test_state_vif.get() == expected

    @pytest.mark.sanity
    def test_vci_state_get_not_running(
            self, mock_pydbus, test_state,
            tmp_file_keepalived_config):
        test_state._conf_obj = tmp_file_keepalived_config

        expected = {}
        assert test_state.get() == expected

    @pytest.mark.sanity
    def test_vci_config_get_with_syncgroup(
            self, mock_pydbus, test_config, syncgroup_config,
            tmp_file_syncgroup_keepalived_config):
        test_config._conf_obj = tmp_file_syncgroup_keepalived_config

        expected = json.dumps(syncgroup_config)
        assert test_config.get() == expected

    @pytest.mark.sanity
    def test_vci_config_set_no_config(
            self, mock_pydbus, test_config,
            top_level_dictionary):
        test_config.set(top_level_dictionary)
        conf_path = Path(
            test_config._conf_obj.config_file_path())

        expected = False
        assert conf_path.exists() == expected

    @pytest.mark.sanity
    def test_vci_config_set_writes_file(
            self, mock_pydbus, test_config,
            simple_config):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.keepalived_proxy_obj.SubState = "running"
        test_config.set(simple_config)
        conf_path = Path(
            test_config._conf_obj.config_file_path())

        expected = True
        assert conf_path.exists() == expected

    @pytest.mark.sanity
    def test_vci_config_set_writes_correct_config(
            self, mock_pydbus, test_config,
            simple_config, simple_keepalived_config):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.keepalived_proxy_obj.SubState = "running"
        file_path = \
            test_config._conf_obj.config_file_path()
        test_config.set(simple_config)
        conf_path = Path(
            test_config._conf_obj.config_file_path())

        expected = True
        assert conf_path.exists() == expected

        file_contents = ""
        with open(file_path, "r") as file_handle:
            file_contents = file_handle.read()

        expected = simple_keepalived_config
        assert file_contents == expected

    @pytest.mark.sanity
    def test_vci_config_set_writes_correct_syncgroup_config(
            self, mock_pydbus, test_config,
            syncgroup_config, syncgroup_keepalived_config):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.keepalived_proxy_obj.SubState = "running"
        file_path = \
            test_config._conf_obj.config_file_path()
        test_config.set(syncgroup_config)
        conf_path = Path(
            test_config._conf_obj.config_file_path())

        expected = True
        assert conf_path.exists() == expected

        file_contents = ""
        with open(file_path, "r") as file_handle:
            file_contents = file_handle.read()

        expected = syncgroup_keepalived_config
        assert file_contents == expected

    @pytest.mark.sanity
    def test_vci_config_check_local_address(
            self, mock_pydbus, test_config, simple_config,
            interface_yang_name,
            dataplane_yang_name, vrrp_yang_name,
            mock_show_version_rpc_kvm):
        intf = simple_config[interface_yang_name][dataplane_yang_name][0]
        intf[vrrp_yang_name]["vrrp-group"][0]["hello-source-address"] =\
            "127.0.0.1"

        expected = None
        assert test_config.check(simple_config) == expected

    @pytest.mark.sanity
    def test_vci_config_check_local_address_not_ip(
            self, mock_pydbus, test_config, simple_config,
            interface_yang_name,
            dataplane_yang_name, vrrp_yang_name,
            mock_show_version_rpc_kvm):
        import vci  # noqa: F401
        intf = simple_config[interface_yang_name][dataplane_yang_name][0]
        intf[vrrp_yang_name]["vrrp-group"][0]["hello-source-address"] =\
            "test"
        with pytest.raises(Exception) as error:
            test_config.check(simple_config)

        expected = (
            "Misconfigured Hello-source-address [test] must be IPv4 or "
            "IPv6 address"
        )
        assert str(error.value) == expected

        expected = "vyatta-vrrp-v1"
        assert error.value.name == expected

        expected = (
            "/interfaces/dataplane/dp0p1s1/vrrp/vrrp-group"
            "/1/hello-source-address/test"
        )
        assert error.value.path == expected

    @pytest.mark.sanity
    def test_vci_config_check_non_local_address(
            self, mock_pydbus, test_config, simple_config,
            interface_yang_name,
            dataplane_yang_name, vrrp_yang_name):
        import vci  # noqa: F401
        intf = simple_config[interface_yang_name][dataplane_yang_name][0]
        intf[vrrp_yang_name]["vrrp-group"][0]["hello-source-address"] =\
            "10.0.0.1"
        with pytest.raises(Exception) as error:
            test_config.check(simple_config)

        expected = (
            "Hello-source-address [10.0.0.1] must be configured on "
            "the interface"
        )
        assert str(error.value) == expected

        expected = "vyatta-vrrp-v1"
        assert error.value.name == expected

        expected = (
            "/interfaces/dataplane/dp0p1s1/vrrp/vrrp-group"
            "/1/hello-source-address/10.0.0.1"
        )
        assert error.value.path == expected

    @pytest.mark.sanity
    def test_vci_config_set_cleans_up_file(
            self, mock_pydbus, test_config,
            simple_config, top_level_dictionary):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.keepalived_proxy_obj.SubState = "running"

        test_config.set(simple_config)
        conf_path = Path(
            test_config._conf_obj.config_file_path())

        expected = True
        assert conf_path.exists() == expected

        test_config.pc.keepalived_proxy_obj.SubState = "running"
        test_config.set(top_level_dictionary)
        conf_path = Path(
            test_config._conf_obj.config_file_path())

        expected = False
        assert conf_path.exists() == expected

    def test_vci_config_check_simple_config(
            self, mock_pydbus, test_config, simple_config,
            mock_show_version_rpc_kvm):
        expected = None
        assert test_config.check(simple_config) == expected

    def test_vci_config_check_fuller_config(
            self, mock_pydbus, test_config, complex_config,
            mock_show_version_rpc_no_hypervisor):
        expected = None
        assert test_config.check(complex_config) == expected

    @pytest.mark.sanity
    def test_vci_config_check_fuller_config_printed_warnings(
            self, mock_pydbus, test_config, complex_config,
            mock_show_version_rpc_vmware, caplog):
        expected_message = \
            "RFC compatibility is not supported on VMWare"
        caplog.set_level(logging.WARNING, logger="vyatta-vrrp-vci")
        test_config.check(complex_config)
        expected = caplog.text
        assert expected_message in expected

    @pytest.mark.sanity
    def test_vci_config_set_writes_disabled_group(
            self, mock_pydbus, test_config, interface_yang_name,
            autogeneration_string,
            dataplane_yang_name, disabled_group,
            dataplane_interface):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.keepalived_proxy_obj.SubState = "running"
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

        expected = True
        assert conf_path.exists() == expected

        file_contents = ""
        with open(file_path, "r") as file_handle:
            file_contents = file_handle.read()

        expected = autogeneration_string
        assert file_contents == expected

    def test_vci_config_set_writes_correct_v3_config(
            self, mock_pydbus, test_config,
            generic_v3_fast_advert_config,
            simple_v3_keepalived_config):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.keepalived_proxy_obj.SubState = "running"
        file_path = \
            test_config._conf_obj.config_file_path()
        test_config.set(generic_v3_fast_advert_config)
        conf_path = Path(
            test_config._conf_obj.config_file_path())

        expected = True
        assert conf_path.exists() == expected

        file_contents = ""
        with open(file_path, "r") as file_handle:
            file_contents = file_handle.read()

        expected = simple_v3_keepalived_config
        assert file_contents == expected
