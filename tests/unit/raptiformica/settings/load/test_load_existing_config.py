from raptiformica.settings.load import load_existing_config
from tests.testcase import TestCase


class TestLoadExistingConfig(TestCase):
    def setUp(self):
        self.load_json = self.set_up_patch(
            'raptiformica.settings.load.load_json'
        )
        self.load_json.return_value = {}
        self.resolve_prototypes = self.set_up_patch(
            'raptiformica.settings.load.resolve_prototypes'
        )

    def test_load_existing_config_loads_config_file(self):
        load_existing_config('/tmp/mutable_config.json')

        self.load_json.assert_called_once_with(
            '/tmp/mutable_config.json'
        )

    def test_load_existing_config_resolves_prototypes_if_there_are_module_prototypes(self):
        self.load_json.return_value = {
            'compute_types': [],
            'module_prototype': {
                'a': 'prototype'
            }
        }

        ret = load_existing_config('/tmp/mutable_config.json')

        self.resolve_prototypes.assert_called_once_with(
                {'a': 'prototype'},
                self.load_json.return_value
        )
        self.assertEqual(ret, self.resolve_prototypes.return_value)

    def test_load_existing_config_does_not_resolve_prototypes_if_there_are_no_module_prototypes(self):
        ret = load_existing_config('/tmp/mutable_config.json')

        self.assertFalse(self.resolve_prototypes.called)
        self.assertEqual(ret, self.load_json.return_value)
