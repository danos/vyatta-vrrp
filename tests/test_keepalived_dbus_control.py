#! /usr/bin/python3

from pathlib import Path

import pytest  # noqa: F401


class TestKeepalivedDbusControl:

    def test_get_unit_state(self, mock_pydbus):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        expected = "UNKNOWN"
        assert process_control.unit_state() == expected

        process_control.refresh_unit_state()
        expected = "dead"
        assert process_control.unit_state() == expected

    @pytest.mark.sanity
    def test_is_process_running(self, mock_pydbus):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.keepalived_proxy_obj.SubState = "running"

        expected = True
        assert process_control.is_running() == expected

    @pytest.mark.sanity
    def test_start_process(self, mock_pydbus):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()

        expected = False
        assert process_control.is_running() == expected

        process_control.restart_process()
        process_control.keepalived_proxy_obj.SubState = "running"

        expected = True
        assert process_control.is_running() == expected

    def test_close_process(self, mock_pydbus):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.keepalived_proxy_obj.SubState = "running"

        expected = True
        assert process_control.is_running() == expected

        process_control.shutdown_process()
        process_control.keepalived_proxy_obj.SubState = "dead"

        expected = False
        assert process_control.is_running() == expected

    def test_set_default_daemon_arguments(
            self, mock_pydbus, tmp_path):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.systemd_default_file_path = f"{tmp_path}/keepalived"
        process_control.snmpd_conf_file_path = f"{tmp_path}/snmpd.conf"
        conf_path = Path(
            process_control.systemd_default_file_path)
        process_control.set_default_daemon_arguments()

        expected = True
        assert conf_path.exists() == expected

    def test_get_agent_x_socket_snmp_not_running(
            self, mock_pydbus, tmp_path):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.snmpd_conf_file_path = f"{tmp_path}/snmpd.conf"

        expected = "tcp:localhost:705:1"
        assert process_control.get_agent_x_socket() == expected

    def test_get_agent_x_socket_snmp_nondefault_socket(
            self, mock_pydbus, mock_snmp_config, tmp_path):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.snmpd_conf_file_path = f"{tmp_path}/snmpd.conf"

        expected = "udp:localhost:100:1"
        assert process_control.get_agent_x_socket() == expected

    def test_find_recv_intf_no_rfc(
            self, mock_pydbus):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.keepalived_proxy_obj.SubState = "running"

        expected = {"vyatta-vrrp-v1:receive": "",
                    "vyatta-vrrp-v1:group": 0}
        assert process_control.get_rfc_mapping("dp0p1s1") == expected

    def test_find_recv_intf_rfc(
            self, mock_pydbus):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.keepalived_proxy_obj.SubState = "running"

        expected = {"vyatta-vrrp-v1:receive": "dp0p1s1",
                    "vyatta-vrrp-v1:group": 1}
        assert process_control.get_rfc_mapping("dp0vrrp1") == expected

    def test_dump_keepalived_data(
            self, mock_pydbus, tmp_path):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        import vyatta.vrrp_vci.keepalived.util as util
        util.FILE_PATH_KEEPALIVED_DATA = f"{tmp_path}/keepalived.data"
        process_control = process_ctrl.ProcessControl()
        process_control.keepalived_proxy_obj.SubState = "running"

        expected = True
        assert process_control.dump_keepalived_data() == expected

    def test_dump_keepalived_stats(
            self, mock_pydbus, tmp_path):
        import vyatta.vrrp_vci.keepalived.dbus.process_control as process_ctrl
        import vyatta.vrrp_vci.keepalived.util as util
        util.FILE_PATH_KEEPALIVED_STATS = f"{tmp_path}/keepalived.stats"
        process_control = process_ctrl.ProcessControl()
        process_control.keepalived_proxy_obj.SubState = "running"

        expected = True
        assert process_control.dump_keepalived_stats() == expected
