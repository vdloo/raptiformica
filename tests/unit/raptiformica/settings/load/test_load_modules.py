from raptiformica.settings.load import load_modules
from tests.testcase import TestCase


class TestLoadModules(TestCase):
    def setUp(self):
        self.load_module_configs = self.set_up_patch(
            'raptiformica.settings.load.load_module_configs'
        )
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
        load_modules(modules_dir='/tmp/a/modules/dir')

        self.load_module_configs.assert_called_once_with(
            modules_dir='/tmp/a/modules/dir'
        )

    def test_load_modules_composes_module_prototypes(self):
        load_modules(modules_dir='/tmp/a/modules/dir')

        self.compose_module_prototypes.assert_called_once_with(
            self.load_module_configs.return_value
        )

    def test_load_modules_finds_module_name_in_module_configs_recursively(self):
        load_modules(modules_dir='/tmp/a/modules/dir')

        self.find_key_in_module_configs_recursively.assert_called_once_with(
            self.load_module_configs.return_value, 'module_name'
        )

    def test_load_modules_returns_loaded_modules(self):
        ret = load_modules(modules_dir='/tmp/a/modules/dir')

        self.assertEqual(
                ret,
                {
                    'value1': (
                        self.load_module_configs.return_value,
                        'value1'
                    ),
                    'value2': (
                        self.load_module_configs.return_value,
                        'value2'
                    ),
                    'value3': (
                        self.load_module_configs.return_value,
                        'value3'
                    ),
                    'module_prototype': self.compose_module_prototypes.return_value
                }
        )
