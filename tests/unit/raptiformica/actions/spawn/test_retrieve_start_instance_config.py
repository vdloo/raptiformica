from raptiformica.actions.spawn import retrieve_start_instance_config
from tests.testcase import TestCase


class TestRetrieveStartInstanceConfig(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.spawn.log')
        self.load_config = self.set_up_patch('raptiformica.actions.spawn.load_config')
        self.config = {
            'compute_types': {
                'vagrant': {
                    'headless': {
                        "source": "https://github.com/vdloo/vagrantfiles",
                        "start_instance_command": "cd headless && vagrant up --provider=virtualbox",
                        "hostname_get_command": "cd headless && vagrant ssh-config | grep HostName | awk '{print$NF}'",
                        "port_get_command": "cd headless && vagrant ssh-config | grep Port | awk '{print$NF}'"
                    }
                }
            }
        }
        self.load_config.return_value = self.config

    def test_retrieve_start_instance_config_logs_retrieving_instance_config_message(self):
        retrieve_start_instance_config(server_type='headless', compute_type='vagrant')

        self.assertTrue(self.log.debug.called)

    def test_retrieve_start_instance_config_exits_with_nonzero_exit_code_when_server_type_not_in_compute_config(self):
        with self.assertRaises(SystemExit):
            retrieve_start_instance_config(server_type='doesnotexist', compute_type='vagrant')

        self.assertTrue(self.log.error.called)

    def test_retrieve_start_instance_config_returns_start_instance_config_for_server_type(self):
        source, start_instance_command, get_hostname_command, get_port_command = retrieve_start_instance_config(
            server_type='headless', compute_type='vagrant'
        )

        self.assertEqual(source, 'https://github.com/vdloo/vagrantfiles')
        self.assertEqual(start_instance_command, 'cd headless && vagrant up --provider=virtualbox')
        self.assertEqual(get_hostname_command, "cd headless && vagrant ssh-config | grep HostName | awk '{print$NF}'")
        self.assertEqual(get_port_command, "cd headless && vagrant ssh-config | grep Port | awk '{print$NF}'")
