from raptiformica.actions.prune import list_compute_checkouts_by_server_type_and_compute_type
from tests.testcase import TestCase


class TestListComputeCheckoutsByServerTypeAndComputeType(TestCase):
    def setUp(self):
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
            },
            'server_types': {
                'headless': {},
                'workstation': {},
                'htpc': {}
            }
        }
        self.prune_load_config = self.set_up_patch('raptiformica.actions.prune.load_config')
        self.prune_load_config.return_value = self.config
        self.list_compute_checkouts_for_server_type_of_compute_type = self.set_up_patch(
            'raptiformica.actions.prune.list_compute_checkouts_for_server_type_of_compute_type'
        )
        self.list_compute_checkouts_for_server_type_of_compute_type.side_effect = \
            lambda server_type, compute_type: [(server_type, compute_type, '/a/directory')] * 5

    def test_list_compute_checkouts_by_server_type_and_compute_type_lists_compute_checkouts(self):
        ret = list_compute_checkouts_by_server_type_and_compute_type()

        expected_compute_checkouts = [
            ('headless', 'docker', '/a/directory'),
            ('workstation', 'docker', '/a/directory'),
            ('headless', 'vagrant', '/a/directory'),

        ] * 5
        self.assertCountEqual(ret, expected_compute_checkouts)

    def test_list_compute_checkouts_by_server_type_and_compute_type_lists_compute_checkouts_if_no_compute_checkouts(self):
        self.list_compute_checkouts_for_server_type_of_compute_type.return_value = []
        self.list_compute_checkouts_for_server_type_of_compute_type.side_effect = None

        ret = list_compute_checkouts_by_server_type_and_compute_type()

        expected_compute_checkouts = []
        self.assertCountEqual(ret, expected_compute_checkouts)
