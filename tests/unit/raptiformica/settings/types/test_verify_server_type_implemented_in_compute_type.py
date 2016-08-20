from raptiformica.settings.types import verify_server_type_implemented_in_compute_type
from tests.testcase import TestCase


class TestVerifyServerTypeImplementedInComputeType(TestCase):
    def setUp(self):
        self.compute_types = {
            'compute_types': {
                'vagrant': {
                    'check_available_command': {'content': '/bin/false'}
                },
                'docker': {},
                'some_other_compute_type': {
                    'check_available_command': {'content': '/bin/true'}
                }
            }
        }

    def test_verify_server_type_implemented_in_compute_type_returns_server_type_implementation_config(self):
        ret = verify_server_type_implemented_in_compute_type(self.compute_types, 'vagrant')

        expected_server_type_implementation_config = {
            'check_available_command': {'content': '/bin/false'}
        }
        self.assertEqual(ret, expected_server_type_implementation_config)

    def test_verify_server_type_implemented_in_compute_type_raises_system_exit_if_server_type_not_implemented(self):
        with self.assertRaises(SystemExit):
            verify_server_type_implemented_in_compute_type(self.compute_types, 'does_not_exist')
