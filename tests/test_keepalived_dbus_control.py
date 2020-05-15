#! /usr/bin/python3

from pathlib import Path

import pytest  # noqa: F401


class TestKeepalivedDbusControl:

    def test_get_unit_state(self, mock_pydbus):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        assert process_control.unit_state() == "UNKNOWN"
        process_control.refresh_unit_state()
        assert process_control.unit_state() == "dead"

    @pytest.mark.sanity
    def test_is_process_running(self, mock_pydbus):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.keepalived_proxy_obj.SubState = "running"
        assert process_control.is_running() is True

    @pytest.mark.sanity
    def test_start_process(self, mock_pydbus):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        assert process_control.is_running() is False
        process_control.restart_process()
        process_control.keepalived_proxy_obj.SubState = "running"
        assert process_control.is_running() is True

    def test_close_process(self, mock_pydbus):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.keepalived_proxy_obj.SubState = "running"
        assert process_control.is_running() is True
        process_control.shutdown_process()
        process_control.keepalived_proxy_obj.SubState = "dead"
        assert process_control.is_running() is False

    def test_set_default_daemon_arguments(
            self, mock_pydbus, tmp_path):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.systemd_default_file_path = f"{tmp_path}/keepalived"
        process_control.snmpd_conf_file_path = f"{tmp_path}/snmpd.conf"
        conf_path = Path(
            process_control.systemd_default_file_path)
        expected = True
        process_control.set_default_daemon_arguments()
        result = conf_path.exists()
        assert expected == result

    def test_get_agent_x_socket_snmp_not_running(
            self, mock_pydbus, tmp_path):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.snmpd_conf_file_path = f"{tmp_path}/snmpd.conf"
        expected = "tcp:localhost:705:1"
        result = process_control.get_agent_x_socket()
        assert expected == result

    def test_get_agent_x_socket_snmp_nondefault_socket(
            self, mock_pydbus, mock_snmp_config, tmp_path):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        process_control.snmpd_conf_file_path = f"{tmp_path}/snmpd.conf"
        expected = "udp:localhost:100:1"
        result = process_control.get_agent_x_socket()
        assert expected == result

    def test_find_recv_intf_no_rfc(
            self, mock_pydbus):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        expected = {"vyatta-vrrp-v1:receive": "",
                    "vyatta-vrrp-v1:group": 0}
        result = process_control.get_rfc_mapping("dp0p1s1")
        assert expected == result

    def test_find_recv_intf_rfc(
            self, mock_pydbus):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        process_control = process_ctrl.ProcessControl()
        expected = {"vyatta-vrrp-v1:receive": "dp0p1s1",
                    "vyatta-vrrp-v1:group": 1}
        result = process_control.get_rfc_mapping("dp0vrrp1")
        assert expected == result

    def test_dump_keepalived_data(
            self, mock_pydbus, tmp_path):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        import vyatta.keepalived.util as util
        util.KEEPALIVED_DATA_FILE_PATH = f"{tmp_path}/keepalived.data"
        process_control = process_ctrl.ProcessControl()
        result = process_control.dump_keepalived_data()
        expected = True
        assert result == expected

    def test_dump_keepalived_stats(
            self, mock_pydbus, tmp_path):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        import vyatta.keepalived.util as util
        util.KEEPALIVED_STATS_FILE_PATH = f"{tmp_path}/keepalived.stats"
        process_control = process_ctrl.ProcessControl()
        result = process_control.dump_keepalived_stats()
        expected = True
        assert result == expected
