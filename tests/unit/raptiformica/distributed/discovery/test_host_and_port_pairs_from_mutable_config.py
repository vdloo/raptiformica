from raptiformica.distributed.discovery import host_and_port_pairs_from_mutable_config
from raptiformica.settings import MUTABLE_CONFIG
from tests.testcase import TestCase


class TestHostAndPortPairsFromMutableConfig(TestCase):
    def setUp(self):
        self.load_config = self.set_up_patch('raptiformica.distributed.discovery.load_config')
        self.load_config.return_value = {
            'meshnet': {
                'neighbours': {
                    'publicKey1': {'host': '1.2.3.4', 'ssh_port': 2222},
                    'publicKey2': {'host': '5.6.7.8', 'ssh_port': 22},
                }
            }
        }

    def test_host_and_port_pairs_from_mutable_config_loads_config_from_mutable_config(self):
        host_and_port_pairs_from_mutable_config()

        self.load_config.assert_called_once_with(MUTABLE_CONFIG)

    def test_host_and_port_pairs_from_mutable_config_returns_host_and_ssh_port_pairs(self):
        ret = host_and_port_pairs_from_mutable_config()

        expected_pairs = [
            ('1.2.3.4', 2222),
            ('5.6.7.8', 22)
        ]
        self.assertCountEqual(ret, expected_pairs)

