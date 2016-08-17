from raptiformica.settings.load import compose_types
from tests.testcase import TestCase


class TestComposeTypes(TestCase):
    def setUp(self):
        self.find_key_in_module_configs_recursively = self.set_up_patch(
            'raptiformica.settings.load.find_key_in_module_configs_recursively'
        )
        # pretend an iterator is returned
        self.find_key_in_module_configs_recursively.return_value = range(0, 10)
        self.merge_module_types = self.set_up_patch(
            'raptiformica.settings.load.merge_module_types'
        )
        self.resolve_prototypes = self.set_up_patch(
            'raptiformica.settings.load.resolve_prototypes'
        )
        self.prototypes = {
            'prototype_name_1': {},
        }
        self.configs = [{}, {}]

    def test_compose_types_finds_key_in_module_configs_recursively(self):
        compose_types(self.prototypes, self.configs, 'a_type')

        self.find_key_in_module_configs_recursively.assert_called_once_with(
            self.configs, 'a_type'
        )

    def test_compose_types_merges_module_types(self):
        compose_types(self.prototypes, self.configs, 'a_type')

        self.merge_module_types.assert_called_once_with(
            list(self.find_key_in_module_configs_recursively.return_value)
        )

    def test_compose_types_resolves_prototypes(self):
        compose_types(self.prototypes, self.configs, 'a_type')

        self.resolve_prototypes.assert_called_once_with(
            self.prototypes,  self.merge_module_types.return_value
        )

    def test_compose_types_returns_resolved_prototypes(self):
        ret = compose_types(self.prototypes, self.configs, 'a_type')

        self.assertEqual(ret, self.resolve_prototypes.return_value)
