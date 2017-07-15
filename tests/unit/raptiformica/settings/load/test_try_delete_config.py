from urllib.error import URLError

from raptiformica.settings.load import try_delete_config
from tests.testcase import TestCase


class TestTryDeleteConfig(TestCase):
    def setUp(self):
        self.delete = self.set_up_patch(
            'raptiformica.settings.load.consul_conn.delete'
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
        self.get_config = self.set_up_patch(
            'raptiformica.settings.load.get_config_mapping',
            return_value=self.mapping
        )
        self.get_config.return_value = self.mapping
        self.cache_config = self.set_up_patch(
            'raptiformica.settings.load.cache_config_mapping'
        )
        self.sync_shared_config_mapping = self.set_up_patch(
            'raptiformica.settings.load.sync_shared_config_mapping'
        )

    def test_try_delete_config_deletes_key_pair_from_distributed_kv_store(self):
        try_delete_config('some/key')

        self.delete.assert_called_once_with(
            'some/key',
            recurse=False
        )

    def test_try_delete_config_syncs_shared_config_mapping(self):
        try_delete_config('some/key')

        self.sync_shared_config_mapping.assert_called_once_with()

    def test_try_delete_config_deletes_key_pair_from_distributed_kv_store_recursively_if_specified(self):
        try_delete_config('some/key', recurse=True)

        self.delete.assert_called_once_with(
            'some/key',
            recurse=True
        )

    def test_try_delete_config_gets_config_if_can_not_connect_to_shared_key_value_store(self):
        self.delete.side_effect = URLError('reason')

        try_delete_config('key')

        self.get_config.assert_called_once_with()

    def test_try_delete_config_caches_config_without_key_if_can_not_connect_to_shared_key_value_store(self):
        self.delete.side_effect = URLError('reason')

        try_delete_config('raptiformica/meshnet/neighbours/a_pubkey.k/uuid')

        del self.mapping[
            'raptiformica/meshnet/neighbours/a_pubkey.k/uuid'
        ]
        self.cache_config.assert_called_once_with(self.mapping)

    def test_try_delete_config_caches_config_without_entire_key_tree_if_no_shared_kv_and_recurse_is_specified(self):
        self.delete.side_effect = URLError('reason')

        try_delete_config(
            'raptiformica/meshnet/neighbours/a_pubkey.k/', recurse=True
        )

        del self.mapping['raptiformica/meshnet/neighbours/a_pubkey.k/uuid']
        del self.mapping['raptiformica/meshnet/neighbours/a_pubkey.k/host']
        del self.mapping['raptiformica/meshnet/neighbours/a_pubkey.k/ssh_port']
        del self.mapping[
            'raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_port'
        ]
        del self.mapping[
            'raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_ipv6_address'
        ]
        del self.mapping[
            'raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_public_key'
        ]
        self.cache_config.assert_called_once_with(self.mapping)
