from raptiformica.settings.meshnet import update_neighbours_config
from tests.testcase import TestCase


class TestUpdateNeighboursConfig(TestCase):
    def setUp(self):
        self.cjdns = self.set_up_patch('raptiformica.settings.meshnet.cjdns')
        self.cjdns.get_public_key.return_value = 'a_public_key.k'
        self.cjdns.get_ipv6_address.return_value = 'ipv6_address'
        self.config = {'meshnet': {'neighbours': {}}}
        self.ensure_neighbour_removed_from_config_by_host = self.set_up_patch(
            'raptiformica.settings.meshnet.ensure_neighbour_removed_from_config_by_host'
        )
        self.try_update_config = self.set_up_patch(
            'raptiformica.settings.meshnet.try_update_config_mapping'
        )

    def test_update_neighbours_config_gets_cjdns_public_key_from_remote_host(self):
        update_neighbours_config('1.2.3.4', port=2222)

        self.cjdns.get_public_key.assert_called_once_with('1.2.3.4', port=2222)

    def test_update_neighbours_config_gets_cjdns_ipv6_address_from_remote_host(self):
        update_neighbours_config('1.2.3.4', port=2222)

        self.cjdns.get_ipv6_address.assert_called_once_with('1.2.3.4', port=2222)

    def test_update_neighbours_config_removes_entries_for_the_updated_host(self):
        update_neighbours_config('1.2.3.4', port=2222)

        self.ensure_neighbour_removed_from_config_by_host.assert_called_once_with(
            '1.2.3.4'
        )

    def test_update_neighbours_config_returns_updated_config(self):
        ret = update_neighbours_config('1.2.3.4', port=2222)

        expected_config = {
            'raptiformica/meshnet/neighbours/a_public_key.k/cjdns_ipv6_address': 'ipv6_address',
            'raptiformica/meshnet/neighbours/a_public_key.k/cjdns_port': 4863,
            'raptiformica/meshnet/neighbours/a_public_key.k/cjdns_public_key': 'a_public_key.k',
            'raptiformica/meshnet/neighbours/a_public_key.k/host': '1.2.3.4',
            'raptiformica/meshnet/neighbours/a_public_key.k/ssh_port': 2222

        }
        self.try_update_config.assert_called_once_with(expected_config)
        self.assertEqual(ret, self.try_update_config.return_value)

    def test_update_neighbours_config_returns_updated_config_with_specified_optional_uuid(self):
        ret = update_neighbours_config('1.2.3.4', port=2222, uuid='someuuid1234')

        expected_config = {
            'raptiformica/meshnet/neighbours/a_public_key.k/cjdns_ipv6_address': 'ipv6_address',
            'raptiformica/meshnet/neighbours/a_public_key.k/cjdns_port': 4863,
            'raptiformica/meshnet/neighbours/a_public_key.k/cjdns_public_key': 'a_public_key.k',
            'raptiformica/meshnet/neighbours/a_public_key.k/host': '1.2.3.4',
            'raptiformica/meshnet/neighbours/a_public_key.k/ssh_port': 2222,
            'raptiformica/meshnet/neighbours/a_public_key.k/uuid': 'someuuid1234'
        }
        self.try_update_config.assert_called_once_with(expected_config)
        self.assertEqual(ret, self.try_update_config.return_value)
