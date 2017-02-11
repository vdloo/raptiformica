from mock import call

from raptiformica.actions.prune import _del_neighbour_by_key
from tests.testcase import TestCase


class TestDelNeighbourByKey(TestCase):
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

    def test_del_neighbour_by_key_gets_mapping(self):
        _del_neighbour_by_key('uuid', "some_uuid")

        self.get_config.assert_called_once_with()

    def test_del_neighbour_by_key_removes_neighbour_by_uuid_from_config(self):
        _del_neighbour_by_key('uuid', "eb442c6170694b12b277c9e88d714cf2")

        self.try_delete_config.assert_called_once_with(
            'raptiformica/meshnet/neighbours/a_pubkey.k/',
            recurse=True
        )

    def test_del_neighbour_by_key_removes_all_entries_with_matching_uuid(self):
        # pretend the uuid of the other neighbour is the same as the first,
        # we should then also then remove that entry
        self.mapping[
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/uuid"
        ] = "eb442c6170694b12b277c9e88d714cf2"
        self.get_config.return_value = self.mapping

        _del_neighbour_by_key('uuid', "eb442c6170694b12b277c9e88d714cf2")

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

    def test_del_neighbour_by_key_does_not_remove_any_entries_if_no_uuid_match(self):
        _del_neighbour_by_key('uuid', "not_a_matching_uuid")

        self.assertFalse(self.try_delete_config.called)
