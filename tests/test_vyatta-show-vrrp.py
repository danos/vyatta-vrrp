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
        ],
        ids=[
            "No rfc", "rfc", "rfc sync", "rfc IPAO", "Backup show",
            "Backup track interface", "Backup track interface no weight",
            "Backup track pathmon", "Backup track route",
            "No rfc v3", "Start delay",
        ]
    )
    def test_show_vrrp_detail(self, fakes, show, data):
        import vyatta.show_vrrp_cmds
        result = vyatta.show_vrrp_cmds.show_vrrp_detail(data)
        assert result == show
