from raptiformica.actions.prune import retrieve_prune_instance_config
from tests.testcase import TestCase


class TestRetrievePruneInstanceConfig(TestCase):
    def setUp(self):
        self.types_log = self.set_up_patch('raptiformica.settings.types.log')
        self.prune_log = self.set_up_patch('raptiformica.actions.prune.log')
        self.load_config = self.set_up_patch('raptiformica.settings.types.load_config')
        self.config = {
            'compute_types': {
                'docker': {
                    'headless': {
                        "detect_stale_instance_command": {
                            "content": "[ -f ubuntu64/container_id ] && "
                                       "/bin/false || sudo docker ps --no-trunc | "
                                       "grep -f ubuntu64/container_id"
                        },
                        "clean_up_instance_command": {
                            "content": "[ -f ubuntu64/container_id ] && "
                                       "cat ubuntu64/container_id | "
                                       "xargs sudo docker rm -f || /bin/true"
                        },
                    },
                    'workstation': {}
                },
            }
        }
        self.load_config.return_value = self.config

    def test_retrieve_prune_instance_config_logs_retrieving_instance_config_message(self):
        retrieve_prune_instance_config(server_type='headless', compute_type='docker')

        self.assertTrue(self.prune_log.debug.called)

    def test_retrieve_prune_instance_config_exits_with_nonzero_exit_code_when_server_type_not_in_compute_config(self):
        with self.assertRaises(SystemExit):
            retrieve_prune_instance_config(server_type='doesnotexist', compute_type='docker')

        self.assertTrue(self.types_log.error.called)

    def test_retrieve_prune_instance_config_returns_prune_instance_config_for_server_type(self):
        detect_stale_instance_command, clean_up_instance_command = retrieve_prune_instance_config(
                server_type='headless', compute_type='docker'
        )

        self.assertEqual(
            detect_stale_instance_command,
            self.config['compute_types']['docker']['headless']['detect_stale_instance_command']['content']
        )
        self.assertEqual(
            clean_up_instance_command,
            self.config['compute_types']['docker']['headless']['clean_up_instance_command']['content']
        )

    def test_retrieve_prune_instance_config_returns_noop_commands_for_unspecified_configs(self):
        config = {
            'compute_types': {
                'docker': {
                    'headless': {}
                }
            }
        }
        self.load_config.return_value = config

        detect_stale_instance_command, clean_up_instance_command = retrieve_prune_instance_config(
            server_type='headless', compute_type='docker'
        )

        self.assertEqual(detect_stale_instance_command, '/bin/true')
        self.assertEqual(clean_up_instance_command, '/bin/true')
