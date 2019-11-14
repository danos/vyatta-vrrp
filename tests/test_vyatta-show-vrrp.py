#! /usr/bin/python3


import pytest


class TestVyattaShowVrrp:

    # pylint: disable=protected-access
    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=too-many-arguments

    @pytest.mark.parametrize(
        "fakes,show,state",
        [
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_show_summary"),
                pytest.lazy_fixture("simple_state")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_rfc_show_summary"),
                pytest.lazy_fixture("simple_rfc_state")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_rfc_sync_show_summary"),
                pytest.lazy_fixture("simple_rfc_sync_state")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_rfc_ipao_show_summary"),
                pytest.lazy_fixture("simple_rfc_ipao_state")
            ),
        ],
        ids=["No rfc", "rfc", "rfc sync", "rfc IPAO"]
    )
    def test_show_vrrp_summary(self, fakes, show, state):
        import vyatta.show_vrrp_cmds
        result = vyatta.show_vrrp_cmds.show_vrrp_summary(state)  # type: str
        assert result == show

    @pytest.mark.parametrize(
        "fakes,show,data",
        [
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_show_detail"),
                pytest.lazy_fixture("detailed_simple_state")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_rfc_show_detail"),
                pytest.lazy_fixture("detailed_simple_rfc_state")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_rfc_sync_show_detail"),
                pytest.lazy_fixture(
                    "detailed_simple_rfc_sync_state"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_rfc_ipao_show_detail"),
                pytest.lazy_fixture(
                    "detailed_simple_rfc_ipao_state"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_generic_group_show_detail"
                ),
                pytest.lazy_fixture(
                    "detailed_backup_simple_state"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_generic_group_track_intf_show_detail"
                ),
                pytest.lazy_fixture(
                    "detailed_backup_track_intf_simple_state"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_generic_group_track_intf_no_weight" +
                    "_show_detail"
                ),
                pytest.lazy_fixture(
                    "detailed_backup_track_intf_no_weight_simple_state"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_generic_group_track_pathmon" +
                    "_show_detail"
                ),
                pytest.lazy_fixture(
                    "detailed_backup_track_pathmon_simple_state"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_generic_group_track_route_show_detail"
                ),
                pytest.lazy_fixture(
                    "detailed_backup_track_route_simple_state"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_v3_group_show_detail"),
                pytest.lazy_fixture("detailed_v3_simple_state")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_start_delay_group_show_detail"),
                pytest.lazy_fixture("detailed_start_delay_simple_state")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_preempt_delay_group_show_detail"),
                pytest.lazy_fixture("detailed_preempt_delay_simple_state")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("multi_group_sync_group_show_detailed"),
                pytest.lazy_fixture("detailed_simple_multi_sync_state")
            ),
        ],
        ids=[
            "No rfc", "rfc", "rfc sync", "rfc IPAO", "Backup show",
            "Backup track interface", "Backup track interface no weight",
            "Backup track pathmon", "Backup track route",
            "No rfc v3", "Start delay",
            "Preempt delay", "Multiple groups in sync-group"
        ]
    )
    def test_show_vrrp_detail(self, fakes, show, data):
        import vyatta.show_vrrp_cmds
        result = vyatta.show_vrrp_cmds.show_vrrp_detail(data)
        assert result == show

    @pytest.mark.parametrize(
        "fakes,show,data",
        [
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_sync_group_show_sync"),
                pytest.lazy_fixture("simple_sync_group_state")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("no_sync_group_show_sync"),
                pytest.lazy_fixture("detailed_v3_simple_state")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_sync_group_show_sync"),
                pytest.lazy_fixture("detailed_simple_multi_sync_state")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("multiple_sync_group_show_sync"),
                pytest.lazy_fixture("multiple_simple_sync_group_state")
            ),
        ],
        ids=[
                "Simple sync group case", "Show vrrp sync without sync group",
                "Simple sync group as part of a larger state dict",
                "Multiple sync groups"
            ]
    )
    def test_show_vrrp_sync(self, fakes, show, data):
        import vyatta.show_vrrp_cmds
        result = vyatta.show_vrrp_cmds.show_vrrp_sync(data)
        assert result == show
