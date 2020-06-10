# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only.

import pytest


class TestVyattaShowVrrp:

    # pylint: disable=protected-access
    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=too-many-arguments

    @pytest.mark.parametrize(
        "fakes,expected,state",
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
                pytest.lazy_fixture("switch_show_vrrp_output"),
                pytest.lazy_fixture("switch_show_dictionary")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_vif_show_summary"),
                pytest.lazy_fixture("simple_vif_state")
            ),
        ],
        ids=["No rfc", "rfc", "rfc sync", "rfc IPAO", "Switch", "vif"]
    )
    def test_show_vrrp_summary(self, fakes, expected, state):
        import vyatta.vrrp_vci.show_vrrp_cmds
        assert vyatta.vrrp_vci.show_vrrp_cmds.show_vrrp_summary(state) \
            == expected

    @pytest.mark.parametrize(
        "fakes,expected,data",
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
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_vif_show_detail"),
                pytest.lazy_fixture("detailed_vif_simple_state")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "generic_v3_rfc_group_fast_advert_show_detail"
                ),
                pytest.lazy_fixture("detailed_v3_rfc_fast_advert_simple_state")
            ),
        ],
        ids=[
            "No rfc", "rfc", "rfc sync", "rfc IPAO", "Backup show",
            "Backup track interface", "Backup track interface no weight",
            "Backup track pathmon", "Backup track route",
            "No rfc v3", "Start delay",
            "Preempt delay", "Multiple groups in sync-group", "Vif",
            "RFC v3 with fast advert",
        ]
    )
    def test_show_vrrp_detail(self, fakes, expected, data):
        import vyatta.vrrp_vci.show_vrrp_cmds
        assert vyatta.vrrp_vci.show_vrrp_cmds.show_vrrp_detail(data) \
            == expected

    @pytest.mark.parametrize(
        "fakes,expected,data,grp_filter",
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
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_sync_group_vif_show_sync"),
                pytest.lazy_fixture("simple_vif_sync_group_state"),
                ""
            ),
        ],
        ids=[
            "Simple sync group case", "Show vrrp sync without sync group",
            "Simple sync group as part of a larger state dict",
            "Multiple sync groups", "show vrrp sync group <blah>",
            "show vrrp sync group doesn't exist", "Vif sync groups"
        ]
    )
    def test_show_vrrp_sync(self, fakes, expected, data, grp_filter):
        import vyatta.vrrp_vci.show_vrrp_cmds
        assert vyatta.vrrp_vci.show_vrrp_cmds.show_vrrp_sync(data, grp_filter)\
            == expected

    @pytest.mark.parametrize(
        "fakes,expected,data,intf_filter,grp_filter",
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
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_vif_show_detail"),
                pytest.lazy_fixture("detailed_vif_simple_state_multiple_intf"),
                "dp0p1s1.10",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_show_detail"),
                pytest.lazy_fixture("detailed_vif_simple_state_multiple_intf"),
                "dp0p1s1",
                ""
            ),
        ],
        ids=[
            "Get all groups on interface", "VRRP not running on interface",
            "No Matching VRRP group",
            "Looking for group when no VRRP is configured on interface",
            "One group on an interface", "All groups on an interface",
            "All groups on a VIF interface",
            "Filter on parent interface group with VIF groups configured"
        ]
    )
    def test_show_vrrp_interface(
            self, fakes, expected, data, intf_filter, grp_filter):
        import vyatta.vrrp_vci.show_vrrp_cmds
        assert \
            vyatta.vrrp_vci.show_vrrp_cmds.show_vrrp_interface(
                data, intf_filter, grp_filter) == expected

    @pytest.mark.parametrize(
        "fakes,expected,data,intf_filter,grp_filter",
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
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_vif_show_stats"),
                pytest.lazy_fixture("generic_group_vif_complete_stats_dict"),
                "",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "generic_group_vif_and_parent_show_stats"
                ),
                pytest.lazy_fixture(
                    "generic_group_vif_and_parent_complete_stats_dict"
                ),
                "",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "generic_group_vif_show_stats"
                ),
                pytest.lazy_fixture(
                    "generic_group_vif_and_parent_complete_stats_dict"
                ),
                "dp0p1s1.10",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "generic_group_show_stats"
                ),
                pytest.lazy_fixture(
                    "generic_group_vif_and_parent_complete_stats_dict"
                ),
                "dp0p1s1",
                ""
            ),
        ],
        ids=[
            "Show stats", "Backup group", "Multi Groups",
            "Full interface",
            "VRRP not running on interface",
            "No matching group on this interface",
            "Multiple interfaces",
            "Vif interface", "Vif and Parent interface",
            "Filter on vif interface", "Filter on parent interface"
        ]
    )
    def test_show_vrrp_statistics(
            self, fakes, expected, data, intf_filter, grp_filter):
        import vyatta.vrrp_vci.show_vrrp_cmds
        assert vyatta.vrrp_vci.show_vrrp_cmds.show_vrrp_statistics_filters(
            data, intf_filter, grp_filter) == expected

    @pytest.mark.parametrize(
        "fakes,expected,file_content",
        [
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("detailed_simple_state"),
                pytest.lazy_fixture("generic_group_simple_keepalived_data")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("detailed_simple_rfc_state"),
                pytest.lazy_fixture("generic_group_rfc_simple_keepalived_data")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_simple_rfc_sync_state"
                ),
                pytest.lazy_fixture("generic_group_rfc_sync_keepalived_data")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_simple_rfc_ipao_state"
                ),
                pytest.lazy_fixture(
                    "generic_group_ipao_rfc_simple_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("detailed_start_delay_simple_state"),
                pytest.lazy_fixture(
                    "generic_group_start_delay_simple_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("detailed_preempt_delay_simple_state"),
                pytest.lazy_fixture(
                    "generic_group_preempt_delay_simple_keepalived_data"
                ),
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("detailed_v3_simple_state"),
                pytest.lazy_fixture("generic_v3_group_simple_keepalived_data")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("detailed_vif_simple_state"),
                pytest.lazy_fixture("generic_group_vif_simple_keepalived_data")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_simple_state"
                ),
                pytest.lazy_fixture(
                    "backup_generic_group_simple_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_track_intf_simple_state"
                ),
                pytest.lazy_fixture(
                    "backup_generic_group_track_intf_simple_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_track_intf_no_weight_simple_state"
                ),
                pytest.lazy_fixture(
                    "backup_generic_group_track_intf_no_weight_simple" +
                    "_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_track_pathmon_simple_state"
                ),
                pytest.lazy_fixture(
                    "backup_generic_group_track_pathmon_simple_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_track_multiple_pathmon_simple_state"
                ),
                pytest.lazy_fixture(
                    "backup_generic_group_multiple_track_pathmon_simple_" +
                    "keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_track_route_simple_state"
                ),
                pytest.lazy_fixture(
                    "backup_generic_group_track_route_simple_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_track_multiple_simple_state"
                ),
                pytest.lazy_fixture(
                    "generic_group_track_multiple_simple_keepalived_data"
                )
            ),
        ],
        ids=[
            "Simple keepalived data", "simple keepalived rfc data",
            "Simple keepalived rfc sync data",
            "Simple keepalived rfc ipao data",
            "Simple keepalived backup data",
            "Simple keepalived with start delay data",
            "Simple keepalived with preempt delay data",
            "Simple keepalived version 3 data",
            "Simple keepalived with vif interface",
            "Complex keepalived backup track intf data",
            "Complex keepalived backup track intf data no weight",
            "Complex keepalived backup track pathmon data",
            "Complex keepalived backup track multiple pathmon data",
            "Complex keepalived backup track route data",
            "Complex keepalived multiple tracked objects data"
        ]
    )
    def test_convert_data_to_json(
            self, fakes, expected, file_content):
        import vyatta.vrrp_vci.show_vrrp_cmds
        assert vyatta.vrrp_vci.show_vrrp_cmds.convert_data_file_to_dict(
            file_content) == expected

    @pytest.mark.parametrize(
        "fakes,expected,file_content",
        [
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_complete_stats_dict"),
                pytest.lazy_fixture("generic_group_keepalived_stats")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("backup_group_complete_stats_dict"),
                pytest.lazy_fixture("backup_group_keepalived_stats"),
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("intf_complete_stats_dict"),
                pytest.lazy_fixture(
                    "master_and_backup_group_keepalived_stats"
                ),
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("multi_intf_complete_stats_dict"),
                pytest.lazy_fixture("multiple_intf_keepalived_stats"),
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "generic_group_vif_complete_stats_dict"
                ),
                pytest.lazy_fixture("generic_group_vif_keepalived_stats")
            ),
        ],
        ids=[
            "Simple keepalived data", "Backup group stats",
            "Multiple group stats", "Multiple interface stats",
            "Vif stats"
        ]
    )
    def test_convert_stats_to_json(
            self, fakes, expected, file_content):
        import vyatta.vrrp_vci.show_vrrp_cmds
        assert vyatta.vrrp_vci.show_vrrp_cmds.convert_stats_file_to_dict(
            file_content) == expected

    @pytest.mark.parametrize(
        "fakes,expected,file_content",
        [
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_show_detail"),
                pytest.lazy_fixture("generic_group_simple_keepalived_data")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_rfc_show_detail"),
                pytest.lazy_fixture("generic_group_rfc_simple_keepalived_data")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_rfc_sync_show_detail"),
                pytest.lazy_fixture(
                    "generic_group_rfc_sync_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_rfc_ipao_show_detail"),
                pytest.lazy_fixture(
                    "generic_group_ipao_rfc_simple_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_generic_group_show_detail"
                ),
                pytest.lazy_fixture(
                    "backup_generic_group_simple_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_generic_group_track_intf_show_detail"
                ),
                pytest.lazy_fixture(
                    "backup_generic_group_track_intf_simple_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_generic_group_track_intf_down_show_detail"
                ),
                pytest.lazy_fixture(
                    "backup_generic_group_track_intf_down_simple_" +
                    "keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_generic_group_track_intf_no_weight"
                    "_show_detail"
                ),
                pytest.lazy_fixture(
                    "backup_generic_group_track_intf_no_weight_simple_"
                    "keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_generic_group_track_pathmon"
                    "_show_detail"
                ),
                pytest.lazy_fixture(
                    "backup_generic_group_track_pathmon_simple_"
                    "keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_backup_generic_group_track_route_show_detail"
                ),
                pytest.lazy_fixture(
                    "backup_generic_group_track_route_simple_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_v3_group_show_detail"),
                pytest.lazy_fixture("generic_v3_group_simple_keepalived_data")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_start_delay_group_show_detail"),
                pytest.lazy_fixture(
                    "generic_group_start_delay_simple_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_preempt_delay_group_show_detail"),
                pytest.lazy_fixture(
                    "generic_group_preempt_delay_simple_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("multi_group_sync_group_show_detailed"),
                pytest.lazy_fixture("sync_group_simple_keepalived_data")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "detailed_generic_group_track_multiple_show_detail"
                ),
                pytest.lazy_fixture(
                    "generic_group_track_multiple_simple_keepalived_data"
                )
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_vif_show_detail"),
                pytest.lazy_fixture("generic_group_vif_simple_keepalived_data")
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "generic_v3_rfc_group_fast_advert_show_detail"
                ),
                pytest.lazy_fixture(
                    "generic_v3_rfc_group_fast_advert_simple_keepalived_data"
                )
            ),
        ],
        ids=[
            "No rfc", "rfc", "rfc sync", "rfc IPAO", "Backup group",
            "Backup group tracked interface",
            "Backup group tracked interface down",
            "Backup group tracked interface no weight",
            "Backup group tracked path monitor",
            "Backup group tracked route",
            "Simple version 3 group",
            "Simple group with start delay",
            "Simple group with preempt delay",
            "Multiple groups with sync groups",
            "Complex group with multiple tracked objects",
            "Vif group", "Version 3 fast-advert"
        ]
    )
    def test_complete_show_vrrp_detail(self, fakes, expected, file_content):
        import vyatta.vrrp_vci.show_vrrp_cmds
        json_data = vyatta.vrrp_vci.show_vrrp_cmds.convert_data_file_to_dict(
            file_content)
        assert vyatta.vrrp_vci.show_vrrp_cmds.show_vrrp_detail(json_data) \
            == expected

    @pytest.mark.parametrize(
        "fakes,expected,file_contents,intf_filter,grp_filter",
        [
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_show_detail"),
                pytest.lazy_fixture("generic_group_simple_keepalived_data"),
                "dp0p1s1",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                "VRRP is not running on dp0p1s2",
                pytest.lazy_fixture("generic_group_simple_keepalived_data"),
                "dp0p1s2",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                "No VRRP group 2 exists on dp0p1s1",
                pytest.lazy_fixture("generic_group_simple_keepalived_data"),
                "dp0p1s1",
                "2"
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                "VRRP is not running on dp0p1s2",
                pytest.lazy_fixture("generic_group_simple_keepalived_data"),
                "dp0p1s2",
                "2"
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "dp0p1s2_vrid_42_show_detail"
                ),
                pytest.lazy_fixture(
                    "multiple_group_simple_keepalived_data"
                ),
                "dp0p1s2",
                "42"
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_vif_show_detail"),
                pytest.lazy_fixture(
                    "generic_group_vif_and_parent_simple_keepalived_data"
                ),
                "dp0p1s1.10",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_show_detail"),
                pytest.lazy_fixture(
                    "generic_group_vif_and_parent_simple_keepalived_data"
                ),
                "dp0p1s1",
                ""
            ),
        ],
        ids=[
            "Get all groups on interface", "VRRP not running on interface",
            "No Matching VRRP group",
            "Looking for group when no VRRP is configured on interface",
            "One group on an interface", "Vif interface filter",
            "Parent interface filter"
        ]
    )
    def test_show_vrrp_interface_full_process(
            self, fakes, expected, file_contents, intf_filter, grp_filter):
        import vyatta.vrrp_vci.show_vrrp_cmds
        json_data = vyatta.vrrp_vci.show_vrrp_cmds.convert_data_file_to_dict(
            file_contents)
        assert vyatta.vrrp_vci.show_vrrp_cmds.show_vrrp_interface(
            json_data, intf_filter, grp_filter) == expected

    @pytest.mark.parametrize(
        "fakes,expected,file_content,grp_filter",
        [
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_sync_group_show_sync"),
                pytest.lazy_fixture("sync_group_simple_keepalived_data"),
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("no_sync_group_show_sync"),
                pytest.lazy_fixture(
                    "generic_group_preempt_delay_simple_keepalived_data"
                ),
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("multiple_sync_group_show_sync"),
                pytest.lazy_fixture(
                    "multiple_sync_groups_simple_keepalived_data"
                ),
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("sync_group_show_sync_group_filter"),
                pytest.lazy_fixture(
                    "multiple_sync_groups_simple_keepalived_data"
                ),
                "TESTV2"
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_sync_group_vif_show_sync"),
                pytest.lazy_fixture("sync_group_simple_vif_keepalived_data"),
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture(
                    "generic_sync_group_vif_and_nonvif_show_sync"
                ),
                pytest.lazy_fixture(
                    "sync_group_simple_vif_and_nonvif_keepalived_data"
                ),
                ""
            ),
        ],
        ids=[
            "Simple sync group case", "No sync groups",
            "Multiple sync groups", "Filter multiple sync groups",
            "Vif interface sync group",
            "Vif and nonvif interface sync group"
        ]
    )
    def test_show_vrrp_sync_full_process(
            self, fakes, expected, file_content, grp_filter):
        import vyatta.vrrp_vci.show_vrrp_cmds
        json_data = \
            vyatta.vrrp_vci.show_vrrp_cmds.convert_data_file_to_dict(
                file_content
            )
        assert vyatta.vrrp_vci.show_vrrp_cmds.show_vrrp_sync(
            json_data, grp_filter) == expected

    @pytest.mark.parametrize(
        "fakes,expected,file_contents,intf_filter,grp_filter",
        [
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_show_stats"),
                pytest.lazy_fixture("generic_group_keepalived_stats"),
                "",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("backup_group_show_stats"),
                pytest.lazy_fixture("backup_group_keepalived_stats"),
                "",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("master_and_backup_group_show_stats"),
                pytest.lazy_fixture(
                    "master_and_backup_group_keepalived_stats"
                ),
                "",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("multiple_intf_show_stats"),
                pytest.lazy_fixture("multiple_intf_keepalived_stats"),
                "",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("master_and_backup_group_show_stats"),
                pytest.lazy_fixture("multiple_intf_keepalived_stats"),
                "dp0p1s1",
                ""
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("filtered_interface_and_group_show_stats"),
                pytest.lazy_fixture("multiple_intf_keepalived_stats"),
                "dp0p1s1",
                "42"
            ),
            (
                pytest.lazy_fixture("calendar_fakes"),
                pytest.lazy_fixture("generic_group_vif_show_stats"),
                pytest.lazy_fixture("generic_group_vif_keepalived_stats"),
                "",
                ""
            ),
        ],
        ids=[
            "Simple keepalived data", "Backup group stats",
            "Multiple group stats", "Multiple interface stats",
            "Filtered stats interface",
            "Filtered stats interface and group",
            "Vif and parent interface stats"
        ]
    )
    def test_show_vrrp_statistics_full_process(
            self, fakes, expected, file_contents, intf_filter, grp_filter):
        import vyatta.vrrp_vci.show_vrrp_cmds
        json_data = vyatta.vrrp_vci.show_vrrp_cmds.convert_stats_file_to_dict(
            file_contents)
        assert vyatta.vrrp_vci.show_vrrp_cmds.show_vrrp_statistics_filters(
            json_data, intf_filter, grp_filter) == expected
