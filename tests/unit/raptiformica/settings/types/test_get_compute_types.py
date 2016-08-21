from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.types import get_compute_types
from tests.testcase import TestCase


class TestGetComputeTypes(TestCase):
    def setUp(self):
        self.settings_load_config = self.set_up_patch('raptiformica.settings.types.load_config')
        self.shell_load_config = self.set_up_patch('raptiformica.shell.types.load_config')
        self.compute_types = {
            'compute_types': {
                'compute_type1': {
                    'check_available_command': {'content': '/bin/false'}
                },
                'compute_type2': {},
                'some_other_compute_type': {
                    'check_available_command': {'content': '/bin/true'}
                }
            }
        }
        self.settings_load_config.return_value = self.compute_types
        self.shell_load_config.return_value = self.compute_types

    def test_get_compute_types_loads_config(self):
        get_compute_types()

        self.settings_load_config.assert_called_once_with(MUTABLE_CONFIG)

    def test_get_compute_types_returns_list_of_compute_types(self):
        ret = get_compute_types()

        self.assertCountEqual(ret, ['compute_type2', 'some_other_compute_type'])

    def test_get_compute_types_returns_empty_list_if_no_compute_types(self):
        self.settings_load_config.return_value = {}

        ret = get_compute_types()

        self.assertCountEqual(ret, [])
