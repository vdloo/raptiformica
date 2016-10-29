from mock import call

from raptiformica.actions.prune import ensure_neighbour_removed_from_config
from tests.testcase import TestCase


class TestEnsureNeighbourRemovedFromConfig(TestCase):
    def setUp(self):
        self.get_config = self.set_up_patch(
            'raptiformica.settings.load.get_config_mapping'
        )
        self.mapping = {
            "raptiformica/meshnet/cjdns/password": "a_secret",
            "raptiformica/meshnet/consul/password": "a_different_secret",
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_ipv6_address": "some_ipv6_address",
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_port": 4863,
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_public_key": "a_pubkey.k",
            "raptiformica/meshnet/neighbours/a_pubkey.k/host": "127.0.0.1",
            "raptiformica/meshnet/neighbours/a_pubkey.k/ssh_port": "2200",
            "raptiformica/meshnet/neighbours/a_pubkey.k/uuid": "eb442c6170694b12b277c9e88d714cf2",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_ipv6_address": "some_other_ipv6_address",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_port": 4863,
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_public_key": "a_different_pubkey.k",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/host": "127.0.0.1",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/ssh_port": "2201",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/uuid": "eb442c6170694b12b277c9e88d714cf1",
        }
        self.get_config.return_value = self.mapping
        self.try_delete_config = self.set_up_patch(
            'raptiformica.actions.prune.try_delete_config'
        )

    def test_ensure_neighbour_removed_from_config_gets_mapping(self):
        ensure_neighbour_removed_from_config("some_uuid")

        self.get_config.assert_called_once_with()

    def test_ensure_neighbour_removed_from_config_removes_neighbour_by_uuid_from_config(self):
        ensure_neighbour_removed_from_config("eb442c6170694b12b277c9e88d714cf2")

        self.try_delete_config.assert_called_once_with(
            'raptiformica/meshnet/neighbours/a_pubkey.k/',
            recurse=True
        )

    def test_ensure_neighbour_removed_from_config_removes_all_entries_with_matching_uuid(self):
        # pretend the uuid of the other neighbour is the same as the first,
        # we should then also then remove that entry
        self.mapping[
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/uuid"
        ] = "eb442c6170694b12b277c9e88d714cf2"
        self.get_config.return_value = self.mapping

        ensure_neighbour_removed_from_config("eb442c6170694b12b277c9e88d714cf2")

        expected_calls = (
            call(
                'raptiformica/meshnet/neighbours/a_pubkey.k/',
                recurse=True
            ),
            call(
                'raptiformica/meshnet/neighbours/a_different_pubkey.k/',
                recurse=True
            )
        )
        self.assertCountEqual(
            self.try_delete_config.mock_calls, expected_calls
        )

    def test_ensure_neighbour_removed_from_config_does_not_remove_any_entries_if_no_uuid_match(self):
        ensure_neighbour_removed_from_config("not_a_matching_uuid")

        self.assertFalse(self.try_delete_config.called)
