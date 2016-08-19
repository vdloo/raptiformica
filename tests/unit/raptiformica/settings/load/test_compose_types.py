from raptiformica.settings.load import compose_types
from tests.testcase import TestCase


class TestComposeTypes(TestCase):
    def setUp(self):
        self.find_key_in_module_configs_recursively = self.set_up_patch(
            'raptiformica.settings.load.find_key_in_module_configs_recursively'
        )
        self.find_key_in_module_configs_recursively.return_value = list()
        self.merge_module_types = self.set_up_patch(
            'raptiformica.settings.load.merge_module_types'
        )
        self.configs = [{}, {}]

    def test_compose_types_finds_key_in_module_configs_recursively(self):
        compose_types(self.configs, 'a_type')

        self.find_key_in_module_configs_recursively.assert_called_once_with(
            self.configs, 'a_type'
        )

    def test_compose_types_merges_module_types(self):
        compose_types(self.configs, 'a_type')

        self.merge_module_types.assert_called_once_with(
            list(self.find_key_in_module_configs_recursively.return_value)
        )

    def test_compose_types_return_merged_module_types(self):
        ret = compose_types(self.configs, 'a_type')

        self.assertEqual(ret, self.merge_module_types.return_value)
