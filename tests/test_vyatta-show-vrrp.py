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
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_rfc_switch_show_summary"),
                pytest.lazy_fixture("simple_rfc_switch_state")
            ),
        ],
        ids=["No rfc", "rfc", "rfc sync", "rfc IPAO", "Switch"]
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
        "fakes,show,data,grp_filter",
        [
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_sync_group_show_sync"),
                pytest.lazy_fixture("simple_sync_group_state"),
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("no_sync_group_show_sync"),
                pytest.lazy_fixture("detailed_v3_simple_state"),
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_sync_group_show_sync"),
                pytest.lazy_fixture("detailed_simple_multi_sync_state"),
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("multiple_sync_group_show_sync"),
                pytest.lazy_fixture("multiple_simple_sync_group_state"),
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("sync_group_show_sync_group_filter"),
                pytest.lazy_fixture("multiple_simple_sync_group_state"),
                "TESTV2"
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "sync_group_show_sync_group_filter_no_group"
                ),
                pytest.lazy_fixture("multiple_simple_sync_group_state"),
                "TEST1"
            ),
        ],
        ids=[
                "Simple sync group case", "Show vrrp sync without sync group",
                "Simple sync group as part of a larger state dict",
                "Multiple sync groups", "show vrrp sync group <blah>",
                "show vrrp sync group doesn't exist"
            ]
    )
    def test_show_vrrp_sync(self, fakes, show, data, grp_filter):
        import vyatta.show_vrrp_cmds
        result = vyatta.show_vrrp_cmds.show_vrrp_sync(data, grp_filter)
        assert result == show

    @pytest.mark.parametrize(
        "fakes,show,data,intf_filter,grp_filter",
        [
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_show_detail"),
                pytest.lazy_fixture("detailed_simple_state"),
                "dp0p1s1",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                "VRRP is not running on dp0p1s2",
                pytest.lazy_fixture("detailed_simple_state"),
                "dp0p1s2",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                "No VRRP group 2 exists on dp0p1s1",
                pytest.lazy_fixture("detailed_simple_state"),
                "dp0p1s1",
                "2"
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                "VRRP is not running on dp0p1s2",
                pytest.lazy_fixture("detailed_simple_state"),
                "dp0p1s2",
                "2"
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "dp0p1s2_vrid_42_show_detail"
                ),
                pytest.lazy_fixture("multiple_interfaces_and_groups_state"),
                "dp0p1s2",
                "42"
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "dp0p1s2_full_show_detail"
                ),
                pytest.lazy_fixture("multiple_interfaces_and_groups_state"),
                "dp0p1s2",
                ""
            )
        ],
        ids=[
                "Get all groups on interface", "VRRP not running on interface",
                "No Matching VRRP group",
                "Looking for group when no VRRP is configured on interface",
                "One group on an interface", "All groups on an interface"
            ]
    )
    def test_show_vrrp_interface(
            self, fakes, show, data, intf_filter, grp_filter):
        import vyatta.show_vrrp_cmds
        result = vyatta.show_vrrp_cmds.show_vrrp_interface(
                                                           data,
                                                           intf_filter,
                                                           grp_filter)
        assert result == show

    @pytest.mark.parametrize(
        "fakes,show,data,intf_filter,grp_filter",
        [
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_show_stats"),
                pytest.lazy_fixture("generic_group_complete_stats_dict"),
                "",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("backup_group_show_stats"),
                pytest.lazy_fixture("backup_group_complete_stats_dict"),
                "",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("master_and_backup_group_show_stats"),
                pytest.lazy_fixture("intf_complete_stats_dict"),
                "",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("master_and_backup_group_show_stats"),
                pytest.lazy_fixture("multi_intf_complete_stats_dict"),
                "dp0p1s1",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                "VRRP is not running on dp0p1s2",
                pytest.lazy_fixture("intf_complete_stats_dict"),
                "dp0p1s2",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                "No VRRP group 2 exists on dp0p1s1",
                pytest.lazy_fixture("intf_complete_stats_dict"),
                "dp0p1s1",
                "2"
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("multiple_intf_show_stats"),
                pytest.lazy_fixture("multi_intf_complete_stats_dict"),
                "",
                ""
            )
        ],
        ids=[
                "Show stats", "Backup group", "Multi Groups",
                "Full interface",
                "VRRP not running on interface",
                "No matching group on this interface",
                "Multiple interfaces"
            ]
    )
    def test_show_vrrp_statistics(
            self, fakes, show, data, intf_filter, grp_filter):
        import vyatta.show_vrrp_cmds
        result = vyatta.show_vrrp_cmds.show_vrrp_statistics_filters(
                                                           data,
                                                           intf_filter,
                                                           grp_filter)
        assert result == show
