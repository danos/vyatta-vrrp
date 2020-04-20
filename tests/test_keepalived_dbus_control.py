#! /usr/bin/python3


import pytest  # noqa: F401
from pathlib import Path


class TestKeepalivedDbusControl:

    def test_get_unit_state(self, mock_pydbus):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        assert pc.unit_state() == "UNKNOWN"
        pc.refresh_unit_state()
        assert pc.unit_state() == "dead"

    @pytest.mark.sanity
    def test_is_process_running(self, mock_pydbus):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        pc.keepalived_proxy_obj.SubState = "running"
        assert pc.is_running() is True

    @pytest.mark.sanity
    def test_start_process(self, mock_pydbus):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        assert pc.is_running() is False
        pc.restart_process()
        pc.keepalived_proxy_obj.SubState = "running"
        assert pc.is_running() is True

    def test_close_process(self, mock_pydbus):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        pc.keepalived_proxy_obj.SubState = "running"
        assert pc.is_running() is True
        pc.shutdown_process()
        pc.keepalived_proxy_obj.SubState = "dead"
        assert pc.is_running() is False

    def test_set_default_daemon_arguments(
            self, mock_pydbus, tmp_path):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        pc.systemd_default_file_path = f"{tmp_path}/vyatta-keepalived"
        pc.snmpd_conf_file_path = f"{tmp_path}/snmpd.conf"
        conf_path = Path(
            pc.systemd_default_file_path)
        expected = True
        pc.set_default_daemon_arguments()
        result = conf_path.exists()
        assert expected == result

    def test_get_agent_x_socket_snmp_not_running(
            self, mock_pydbus, tmp_path):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        pc.snmpd_conf_file_path = f"{tmp_path}/snmpd.conf"
        expected = "tcp:localhost:705:1"
        result = pc.get_agent_x_socket()
        assert expected == result

    def test_get_agent_x_socket_snmp_nondefault_socket(
            self, mock_pydbus, mock_snmp_config, tmp_path):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        pc.snmpd_conf_file_path = f"{tmp_path}/snmpd.conf"
        expected = "udp:localhost:100:1"
        result = pc.get_agent_x_socket()
        assert expected == result

    def test_find_recv_intf_no_rfc(
            self, mock_pydbus):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        expected = {"vyatta-vrrp-v1:receive": "",
                    "vyatta-vrrp-v1:group": 0}
        result = pc.get_rfc_mapping("dp0p1s1")
        assert expected == result

    def test_find_recv_intf_rfc(
            self, mock_pydbus):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        pc = process_ctrl.ProcessControl()
        expected = {"vyatta-vrrp-v1:receive": "dp0p1s1",
                    "vyatta-vrrp-v1:group": 1}
        result = pc.get_rfc_mapping("dp0vrrp1")
        assert expected == result

    def test_dump_keepalived_data(
            self, mock_pydbus, tmp_path):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        import vyatta.keepalived.util as util
        util.KEEPALIVED_DATA_FILE_PATH = f"{tmp_path}/keepalived.data"
        pc = process_ctrl.ProcessControl()
        result = pc.dump_keepalived_data()
        expected = True
        assert result == expected

    def test_dump_keepalived_stats(
            self, mock_pydbus, tmp_path):
        import vyatta.keepalived.dbus.process_control as process_ctrl
        import vyatta.keepalived.util as util
        util.KEEPALIVED_STATS_FILE_PATH = f"{tmp_path}/keepalived.stats"
        pc = process_ctrl.ProcessControl()
        result = pc.dump_keepalived_stats()
        expected = True
        assert result == expected
