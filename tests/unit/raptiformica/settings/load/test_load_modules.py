from mock import call

from raptiformica.settings.load import load_modules
from tests.testcase import TestCase


class TestLoadModules(TestCase):
    def setUp(self):
        self.load_module_configs = self.set_up_patch(
            'raptiformica.settings.load.load_module_configs'
        )
        self.load_module_configs.side_effect = [[1, 2, 3], [4, 5, 6]]
        self.compose_module_prototypes = self.set_up_patch(
            'raptiformica.settings.load.compose_module_prototypes'
        )
        self.find_key_in_module_configs_recursively = self.set_up_patch(
            'raptiformica.settings.load.find_key_in_module_configs_recursively'
        )
        self.find_key_in_module_configs_recursively.return_value = [
            ['value1', 'value2'],
            ['value3'],
        ]
        self.compose_types = self.set_up_patch(
            'raptiformica.settings.load.compose_types'
        )
        self.compose_types.side_effect = lambda *args: args

    def test_load_modules_loads_module_configs(self):
        load_modules(modules_dirs=('/tmp/a/modules/dir', '/tmp/a/nother/modules/dir'))

        expected_calls = [
            call('/tmp/a/modules/dir'),
            call('/tmp/a/nother/modules/dir')
        ]
        self.assertCountEqual(self.load_module_configs.mock_calls, expected_calls)

    def test_load_modules_composes_module_prototypes(self):
        load_modules(modules_dirs=('/tmp/a/modules/dir', '/tmp/a/nother/modules/dir'))

        self.compose_module_prototypes.assert_called_once_with(
            [1, 2, 3, 4, 5, 6]
        )

    def test_load_modules_finds_module_name_in_module_configs_recursively(self):
        load_modules(modules_dirs=('/tmp/a/modules/dir', '/tmp/a/nother/modules/dir'))

        self.find_key_in_module_configs_recursively.assert_called_once_with(
            [1, 2, 3, 4, 5, 6], 'module_name'
        )

    def test_load_modules_returns_loaded_modules(self):
        ret = load_modules(modules_dirs=('/tmp/a/modules/dir', '/tmp/a/nother/modules/dir'))

        self.assertEqual(
                ret,
                {
                    'value1': (
                        [1, 2, 3, 4, 5, 6],
                        'value1'
                    ),
                    'value2': (
                        [1, 2, 3, 4, 5, 6],
                        'value2'
                    ),
                    'value3': (
                        [1, 2, 3, 4, 5, 6],
                        'value3'
                    ),
                    'module_prototype': self.compose_module_prototypes.return_value
                }
        )
