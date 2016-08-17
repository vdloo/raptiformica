from raptiformica.actions.prune import register_clean_up_triggers
from tests.testcase import TestCase


class TestRegisterCleanUpTriggers(TestCase):
    def setUp(self):
        self.compute_checkouts = [
            ('headless', 'docker', 'a/docker/checkout/directory1'),
            ('headless', 'docker', 'a/docker/checkout/directory2'),
            ('workstation', 'docker', 'a/docker/checkout/directory3'),
            ('headless', 'vagrant', 'a/vagrant/checkout/directory1')
        ]
        self.load_config = self.set_up_patch('raptiformica.settings.types.load_config')
        self.docker_detect_stale_instance_command = "[ -f ubuntu64/container_id ] && " \
                                                    "/bin/false || sudo docker ps --no-trunc | " \
                                                    "grep -f ubuntu64/container_id"
        self.docker_clean_up_stale_instance_command = "[ -f ubuntu64/container_id ] && " \
                                                      "cat ubuntu64/container_id | " \
                                                      "xargs sudo docker rm -f || /bin/true"
        self.config = {
            'compute_types': {
                'docker': {
                    'headless': {
                        "detect_stale_instance_command": {
                            "content": self.docker_detect_stale_instance_command
                        },
                        "clean_up_instance_command": {
                            "content": self.docker_clean_up_stale_instance_command
                        }
                    },
                    'workstation': {
                        "detect_stale_instance_command": {
                            "content": self.docker_detect_stale_instance_command
                        },
                        "clean_up_instance_command": {
                            "content": self.docker_clean_up_stale_instance_command
                        }
                    }
                },
                'vagrant': {
                    'headless': {}
                }
            }
        }
        self.load_config.return_value = self.config

    def test_register_clean_up_triggers_returns_triggers(self):
        ret = register_clean_up_triggers(self.compute_checkouts)

        expected_triggers = [
            ('a/docker/checkout/directory1',
             self.docker_detect_stale_instance_command,
             self.docker_clean_up_stale_instance_command),
            ('a/docker/checkout/directory2',
             self.docker_detect_stale_instance_command,
             self.docker_clean_up_stale_instance_command),
            ('a/docker/checkout/directory3',
             self.docker_detect_stale_instance_command,
             self.docker_clean_up_stale_instance_command),
            ('a/vagrant/checkout/directory1',
             '/bin/true',
             '/bin/true')
        ]
        self.assertCountEqual(ret, expected_triggers)
