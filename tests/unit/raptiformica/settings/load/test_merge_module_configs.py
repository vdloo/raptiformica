from raptiformica.settings.load import merge_module_configs
from tests.testcase import TestCase


class TestMergeModuleConfigs(TestCase):
    def setUp(self):
        self.configs = [
            {
                'key1': 'value2',
                'key2': 'value4',
                'key3': {
                    'key1': 'value3'
                }
            },
            {
                'key1': 'value6',
                'key4': {
                    'key1': 'value4'
                },
                'key5': 'value5'
            }
        ]

    def test_merge_module_configs_merges_module_configs(self):
        ret = merge_module_configs(self.configs)

        expected_config = {
            'key1': 'value6',
            'key2': 'value4',
            'key3': {
                'key1': 'value3'
            },
            'key4': {
                'key1': 'value4'
            },
            'key5': 'value5'
        }
        self.assertEqual(ret, expected_config)
