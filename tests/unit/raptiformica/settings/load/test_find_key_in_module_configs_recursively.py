from tests.testcase import TestCase

from raptiformica.settings.load import find_key_in_module_configs_recursively


class TestFindKeyInModuleConfigsRecursively(TestCase):
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
                'key4': {
                    'key1': 'value4'
                },
                'key5': 'value5'
            }
        ]

    def test_find_key_in_module_configs_recursively_finds_key_in_dict_recursively(self):
        ret = list(find_key_in_module_configs_recursively(self.configs, 'key1'))

        self.assertCountEqual(ret[0], ['value3', 'value2'])
        self.assertCountEqual(ret[1], ['value4'])
