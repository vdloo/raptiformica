from raptiformica.settings import CJDNS_DEFAULT_PORT
from raptiformica.settings.meshnet import update_neighbours_config
from tests.testcase import TestCase


class TestUpdateNeighboursConfig(TestCase):
    def setUp(self):
        self.cjdns = self.set_up_patch('raptiformica.settings.meshnet.cjdns')
        self.cjdns.get_public_key.return_value = 'a_public_key.k'
        self.cjdns.get_ipv6_address.return_value = 'ipv6_address'
        self.config = {'meshnet': {'neighbours': {}}}

    def test_update_neighbours_config_gets_cjdns_public_key_from_remote_host(self):
        update_neighbours_config(self.config, '1.2.3.4', port=2222)

        self.cjdns.get_public_key.assert_called_once_with('1.2.3.4', port=2222)

    def test_update_neighbours_config_gets_cjdns_ipv6_address_from_remote_host(self):
        update_neighbours_config(self.config, '1.2.3.4', port=2222)

        self.cjdns.get_ipv6_address.assert_called_once_with('1.2.3.4', port=2222)

    def test_update_neighbours_config_returns_updated_config(self):
        ret = update_neighbours_config(self.config, '1.2.3.4', port=2222)

        expected_config = {
            'meshnet': {
                'neighbours': {
                    'a_public_key.k': {
                        'host': '1.2.3.4',
                        'cjdns_port': CJDNS_DEFAULT_PORT,
                        'ssh_port': 2222,
                        'cjdns_public_key': 'a_public_key.k',
                        'cjdns_ipv6_address': 'ipv6_address'
                    }
                }
            }
        }
        self.assertEqual(ret, expected_config)

    def test_update_neighbours_config_returns_updated_config_with_specified_optional_uuid(self):
        ret = update_neighbours_config(self.config, '1.2.3.4', port=2222, uuid='someuuid1234')

        expected_config = {
            'meshnet': {
                'neighbours': {
                    'a_public_key.k': {
                        'host': '1.2.3.4',
                        'cjdns_port': CJDNS_DEFAULT_PORT,
                        'ssh_port': 2222,
                        'cjdns_public_key': 'a_public_key.k',
                        'cjdns_ipv6_address': 'ipv6_address',
                        'uuid': 'someuuid1234'
                    }
                }
            }
        }
        self.assertEqual(ret, expected_config)
