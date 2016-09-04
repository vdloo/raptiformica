from raptiformica.actions.prune import register_clean_up_triggers
from tests.testcase import TestCase


class TestRegisterCleanUpTriggers(TestCase):
    def setUp(self):
        self.compute_checkouts = [
            ('headless', 'docker', 'a/docker/checkout/directory1'),
            ('headless', 'docker', 'a/docker/checkout/directory2'),
        ]
        self.detect_stale_instance_command = "bash -c 'cd ubuntu64 && " \
                                             "[ -f container_id ] && " \
                                             "sudo docker ps --no-trunc | " \
                                             "grep -f container_id'"
        self.clean_up_stale_instance_command = "bash -c 'cd ubuntu64 && " \
                                               "[ -f container_id ] && " \
                                               "cat container_id | " \
                                               "xargs sudo docker rm -f || /bin/true'"
        self.mapping = {
            "raptiformica/compute/docker/headless/available": "docker -v",
            "raptiformica/compute/docker/headless/clean_up_instance_command": self.clean_up_stale_instance_command,
            "raptiformica/compute/docker/headless/detect_stale_instance": self.detect_stale_instance_command,
            "raptiformica/compute/docker/headless/get_port": "echo 22",
            "raptiformica/compute/docker/headless/source": "https://github.com/vdloo/dockerfiles.git",
        }
        self.get_config = self.set_up_patch('raptiformica.actions.mesh.get_config')
        self.get_config.return_value = self.mapping

    def test_register_clean_up_triggers_returns_triggers(self):
        ret = register_clean_up_triggers(self.compute_checkouts)

        expected_triggers = [
            ('a/docker/checkout/directory1',
             self.detect_stale_instance_command,
             self.clean_up_stale_instance_command),
            ('a/docker/checkout/directory2',
             self.detect_stale_instance_command,
             self.clean_up_stale_instance_command),
        ]
        self.assertCountEqual(ret, expected_triggers)
