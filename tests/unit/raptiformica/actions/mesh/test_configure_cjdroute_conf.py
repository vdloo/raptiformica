from mock import call

from raptiformica.actions.mesh import configure_cjdroute_conf, CJDROUTE_CONF_PATH
from tests.testcase import TestCase


class TestConfigureCjdrouteConf(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.mapping = {
            "raptiformica/meshnet/cjdns/password": "a_secret",
            "raptiformica/meshnet/consul/password": "a_different_secret",
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_ipv6_address": "some_ipv6_address",
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_port": 4863,
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_public_key": "a_pubkey.k",
            "raptiformica/meshnet/neighbours/a_pubkey.k/host": "192.168.178.23",
            "raptiformica/meshnet/neighbours/a_pubkey.k/ssh_port": "2200",
            "raptiformica/meshnet/neighbours/a_pubkey.k/uuid": "eb442c6170694b12b277c9e88d714cf2",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_ipv6_address": "some_other_ipv6_address",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_port": 4863,
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_public_key": "a_different_pubkey.k",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/host": "192.168.178.24",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/ssh_port": "2201",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/uuid": "eb442c6170694b12b277c9e88d714cf1",
        }
        self.load_json = self.set_up_patch('raptiformica.actions.mesh.load_json')
        self.load_json.return_value = {
            'interfaces': {
                'UDPInterface': []
            },
            'publicKey': 'yet_another_public_key.k'
        }
        self.get_config = self.set_up_patch('raptiformica.actions.mesh.get_config_mapping')
        self.get_config.return_value = self.mapping
        self.write_json = self.set_up_patch('raptiformica.actions.mesh.write_json')

    def test_configure_cjdroute_conf_logs_configuring_cjdroute_config_message(self):
        configure_cjdroute_conf()

        self.assertTrue(self.log.info.called)

    def test_configure_cjdroute_conf_loads_cjdroute_conf(self):
        configure_cjdroute_conf()

        expected_calls = [call(CJDROUTE_CONF_PATH)] * 2
        self.assertCountEqual(self.load_json.mock_calls, expected_calls)

    def test_configure_cjdroute_conf_writes_cjdroute_config_to_disk(self):
        configure_cjdroute_conf()

        expected_config = {
            'authorizedPasswords': [
                {'password': 'a_secret'}
            ],
            'interfaces': {
                'UDPInterface': [{
                    'connectTo': {
                        '192.168.178.23:4863': {
                            'peerName': '192.168.178.23:4863',
                            'publicKey': 'a_pubkey.k',
                            'password': 'a_secret'
                        },
                        '192.168.178.24:4863': {
                            'peerName': '192.168.178.24:4863',
                            'publicKey': 'a_different_pubkey.k',
                            'password': 'a_secret'
                        }
                    },
                    'bind': '0.0.0.0:4863'
                }]
            },
            'publicKey': 'yet_another_public_key.k'
        }
        self.write_json.assert_called_once_with(
            expected_config,
            CJDROUTE_CONF_PATH
        )

