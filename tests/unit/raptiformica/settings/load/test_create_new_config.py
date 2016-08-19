from raptiformica.settings.load import create_new_config
from tests.testcase import TestCase


class TestCreateNewConfig(TestCase):
    def setUp(self):
        self.load_unresolved_modules = self.set_up_patch(
            'raptiformica.settings.load.load_unresolved_modules'
        )
        self.load_unresolved_modules.return_value = {
            'compute_types': []
        }
        self.write_config = self.set_up_patch(
            'raptiformica.settings.load.write_config'
        )
        self.resolve_prototypes = self.set_up_patch(
            'raptiformica.settings.load.resolve_prototypes'
        )

    def test_create_new_config_loads_unresolved_modules(self):
        create_new_config('/tmp/mutable_config.json')

        self.load_unresolved_modules.assert_called_once_with()

    def test_create_new_config_raises_a_value_error_if_no_valid_config_could_be_constructed(self):
        self.load_unresolved_modules.return_value = {}

        with self.assertRaises(ValueError):
            create_new_config('/tmp/mutable_config.json')

    def test_create_new_config_writes_config_to_file(self):
        create_new_config('/tmp/mutable_config.json')

        self.write_config.assert_called_once_with(
            self.load_unresolved_modules.return_value,
            '/tmp/mutable_config.json'
        )

    def test_create_new_config_resolves_prototypes_if_there_are_module_prototypes(self):
        self.load_unresolved_modules.return_value = {
            'compute_types': [],
            'module_prototype': {
                'a': 'prototype'
            }
        }

        ret = create_new_config('/tmp/mutable_config.json')

        self.resolve_prototypes.assert_called_once_with(
            {'a': 'prototype'},
            self.load_unresolved_modules.return_value
        )
        self.assertEqual(ret, self.resolve_prototypes.return_value)

    def test_create_new_config_does_not_resolve_prototypes_if_there_are_no_module_prototypes(self):
        ret = create_new_config('/tmp/mutable_config.json')

        self.assertFalse(self.resolve_prototypes.called)
        self.assertEqual(ret, self.load_unresolved_modules.return_value)
