from raptiformica.actions.slave import retrieve_provisioning_config
from raptiformica.settings.server import get_first_server_type
from tests.testcase import TestCase


class TestRetrieveProvisioningConfig(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.slave.log')
        self.load_config = self.set_up_patch('raptiformica.actions.slave.load_config')
        self.config = {
            'server_types': {
                'headless': {
                    'source': 'https://github.com/vdloo/puppetfiles',
                    'name': 'puppetfiles',
                    'bootstrap_command': './papply.sh manifests/headless.pp'
                },
                'workstation': {
                    'source': 'https://github.com/vdloo/puppetfiles',
                    'name': 'puppetfiles',
                    'bootstrap_command': './papply.sh manifests/workstation.pp'
                }
            }
        }
        self.load_config.return_value = self.config

    def test_retrieve_provisioning_config_logs_retrieving_config_message(self):
        retrieve_provisioning_config()

        self.log.info.assert_called_once_with("Retrieving provisioning config")

    def test_retrieve_provisioning_config_loads_config(self):
        retrieve_provisioning_config()

        self.load_config.assert_called_once_with()

    def test_retrieve_provisioning_config_returns_provisioning_config(self):
        ret = retrieve_provisioning_config()

        expected_config = (
            self.config['server_types'][get_first_server_type()]['source'],
            self.config['server_types'][get_first_server_type()]['name'],
            self.config['server_types'][get_first_server_type()]['bootstrap_command']
        )
        self.assertEqual(ret, expected_config)

    def test_retrieve_provisioning_config_returns_provisioning_config_for_specified_server_type(self):
        ret = retrieve_provisioning_config(server_type='workstation')

        expected_config = (
            self.config['server_types']['workstation']['source'],
            self.config['server_types']['workstation']['name'],
            self.config['server_types']['workstation']['bootstrap_command']
        )
        self.assertEqual(ret, expected_config)
