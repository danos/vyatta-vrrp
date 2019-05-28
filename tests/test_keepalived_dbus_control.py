#! /usr/bin/python3


import pytest  # noqa: F401


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
