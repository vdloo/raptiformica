from raptiformica.settings.load import merge_module_types
from tests.testcase import TestCase


class TestMergeModuleTypes(TestCase):
    def setUp(self):
        self.merge_module_configs = self.set_up_patch(
            'raptiformica.settings.load.merge_module_configs'
        )
        self.configs = [[{}, {}], [{}]]

    def test_merge_module_types_merges_flattened_module_configs(self):
        merge_module_types(self.configs)

        expected_argument = [{}] * 3
        received_argument = self.merge_module_configs.call_args[0][0]

        self.assertCountEqual(received_argument, expected_argument)
