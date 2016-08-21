from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.types import get_server_types
from tests.testcase import TestCase


class TestGetServerTypes(TestCase):
    def setUp(self):
        self.settings_load_config = self.set_up_patch('raptiformica.settings.types.load_config')
        self.shell_load_config = self.set_up_patch('raptiformica.shell.types.load_config')
        self.server_types = {
            'server_types': {
                'headless': {
                    'check_available_command': {'content': '/bin/false'}
                },
                'workstation': {},
                'htpc': {
                    'check_available_command': {'content': '/bin/true'}
                }
            }
        }
        self.settings_load_config.return_value = self.server_types
        self.shell_load_config.return_value = self.server_types

    def test_get_server_types_loads_config(self):
        get_server_types()

        self.settings_load_config.assert_called_once_with(MUTABLE_CONFIG)

    def test_get_server_types_returns_list_of_server_types(self):
        ret = get_server_types()

        self.assertCountEqual(ret, ['workstation', 'htpc'])

    def test_get_server_types_returns_empty_list_if_no_server_types(self):
        self.settings_load_config.return_value = {}

        ret = get_server_types()

        self.assertCountEqual(ret, [])
