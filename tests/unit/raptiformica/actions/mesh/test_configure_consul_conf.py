from mock import call

from raptiformica.actions.mesh import configure_consul_conf, CJDROUTE_CONF_PATH, CONSUL_CONF_PATH
from tests.testcase import TestCase


class TestConfigureConsulConf(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.mutable_config = {
            'meshnet': {
                'consul': {
                    'password': "the_symmetric_password"
                }
            }
        }
        self.cjdroute_config = {
            'ipv6': 'the_ipv6_address',
        }
        self.load_json = self.set_up_patch('raptiformica.actions.mesh.load_json')
        self.load_json.return_value = self.cjdroute_config
        self.ensure_directory = self.set_up_patch('raptiformica.actions.mesh.ensure_directory')
        self.write_json = self.set_up_patch('raptiformica.actions.mesh.write_json')

    def test_configure_consul_conf_logs_configuring_consul_config_message(self):
        configure_consul_conf(self.mutable_config)

        self.assertTrue(self.log.info.called)

    def test_configure_consul_conf_loads_cjdroute_config(self):
        configure_consul_conf(self.mutable_config)

        self.load_json.assert_called_once_with(CJDROUTE_CONF_PATH)

    def test_configure_consul_conf_ensures_consul_settings_directories_exist(self):
        configure_consul_conf(self.mutable_config)

        expected_calls = [
            call('/etc/consul.d'),
            call('/etc/opt.consul')
        ]
        self.assertTrue(expected_calls, self.ensure_directory.mock_calls)

    def test_configure_consul_conf_writes_generated_consul_conf_to_disk(self):
        configure_consul_conf(self.mutable_config)

        expected_config = {
            'bootstrap_expect': 3,
            'data_dir': '/opt/consul',
            'datacenter': 'raptiformica',
            'log_level': 'INFO',
            'node_name': 'the_ipv6_address',
            'server': True,
            'bind_addr': '::',
            'advertise_addr': 'the_ipv6_address',
            'encrypt': 'the_symmetric_password',
            'disable_remote_exec': False
        }
        self.write_json.assert_called_once_with(
            expected_config,
            CONSUL_CONF_PATH
        )
