from raptiformica.actions.mesh import configure_cjdroute_conf, CJDROUTE_CONF_PATH
from tests.testcase import TestCase


class TestConfigureCjdrouteConf(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.config = {
            'meshnet': {
                'cjdns': {'password': 'the_shared_secret'},
                'neighbours': {
                    'a_public_key1.k': {
                        "cjdns_ipv6_address": "ipv6_address1",
                        "cjdns_public_key": "a_public_key1.k",
                        "host": "192.168.178.23",
                        "port": 4863
                    },
                    'a_public_key2.k': {
                        "cjdns_ipv6_address": "ipv6_address2",
                        "cjdns_public_key": "a_public_key2.k",
                        "host": "192.168.178.24",
                        "port": 4863
                    }
                }
            }
        }
        self.load_json = self.set_up_patch('raptiformica.actions.mesh.load_json')
        self.load_json.return_value = {
            'interfaces': {
                'UDPInterface': []
            }
        }
        self.parse_cjdns_neighbours = self.set_up_patch('raptiformica.actions.mesh.parse_cjdns_neighbours')
        self.write_json = self.set_up_patch('raptiformica.actions.mesh.write_json')

    def test_configure_cjdroute_conf_logs_configuring_cjdroute_config_message(self):
        configure_cjdroute_conf(self.config)

        self.assertTrue(self.log.info.called)

    def test_configure_cjdroute_conf_loads_cjdroute_conf(self):
        configure_cjdroute_conf(self.config)

        self.load_json.assert_called_once_with(CJDROUTE_CONF_PATH)

    def test_configure_cjdroute_conf_parses_cjdns_neighbours(self):
        configure_cjdroute_conf(self.config)

        self.parse_cjdns_neighbours(
            self.config['meshnet']
        )

    def test_configure_cjdroute_conf_writes_cjdroute_config_to_disk(self):
        configure_cjdroute_conf(self.config)

        expected_config = {
            'authorizedPasswords': [
                {'password': 'the_shared_secret'}
            ],
            'interfaces': {
                'UDPInterface': [{
                    'connectTo': self.parse_cjdns_neighbours.return_value,
                    'bind': '0.0.0.0:4863'
                }]
            }
        }
        self.write_json.assert_called_once_with(
            expected_config,
            CJDROUTE_CONF_PATH
        )

