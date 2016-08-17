from raptiformica.settings.load import get_config_value
from tests.testcase import TestCase


class TestGetConfigValue(TestCase):
    def test_get_config_value_gets_config_value(self):
        config = {
            'key1': {'content': 'value1'},
            'key2': {'content': 'value2'},
            'key3': 'value3'
        }
        ret = get_config_value(config, 'key2')

        self.assertEqual(ret, 'value2')

    def test_get_config_value_defaults_to_empty_string_by_default(self):
        ret = get_config_value({}, 'key2')

        self.assertEqual(ret, '')

    def test_get_config_value_defaults_to_default_if_dict(self):
        ret = get_config_value({}, 'key2', default={})

        self.assertEqual(ret, {})

    def test_get_config_value_defaults_to_default_if_list(self):
        ret = get_config_value({}, 'key2', default=[])

        self.assertEqual(ret, [])

    def test_get_config_appends_prototype_config_if_specified(self):
        config = {
            'key1': {'content': 'value1'},
            'key2': {'content': 'value2_1', 'append_prototype_content': True},
            'key3': 'value3',
            'prototype': {
                'key2': {'content': ' && value2_2'}
            }
        }
        ret = get_config_value(config, 'key2')

        self.assertEqual(ret, 'value2_1 && value2_2')

    def test_get_config_finds_nested_keys(self):
        config = {
            'key1': {'key2': {'content': 'value2_1', 'append_prototype_content': True}},
            'key3': 'value3',
            'prototype': {
                'key2': {'content': ' && value2_2'}
            }
        }
        ret = get_config_value(config, 'key2')

        self.assertEqual(ret, 'value2_1 && value2_2')

    def test_get_config_traverses_multiple_levels_of_prototypes(self):
        config = {
            'key1': {'key2': {'content': 'value2_1', 'append_prototype_content': True}},
            'key3': 'value3',
            'prototype': {
                'key1': {'content': 'value1'},
                'key2': {'content': ' && value2_2', 'append_prototype_content': True},
                'key3': 'value3',
                'prototype': {
                    'key2': {'content': ' && value2_3'}
                }
            }
        }
        ret = get_config_value(config, 'key2')

        self.assertEqual(ret, 'value2_1 && value2_2 && value2_3')

    def test_get_config_does_not_append_prototype_by_default(self):
        config = {
            'key1': {'key2': {'content': 'value2_1'}},
            'key3': 'value3',
            'prototype': {
                'key2': {'content': ' && value2_2'}
            }
        }
        ret = get_config_value(config, 'key2')

        self.assertEqual(ret, 'value2_1')

    def test_get_config_does_not_append_prototype_if_specified(self):
        config = {
            'key1': {'key2': {'content': 'value2_1', 'append_prototype': False}},
            'key3': 'value3',
            'prototype': {
                'key2': {'content': ' && value2_2'}
            }
        }
        ret = get_config_value(config, 'key2')

        self.assertEqual(ret, 'value2_1')

    def test_get_config_gets_prototype_content_if_no_matching_value_at_level(self):
        config = {
            'key3': 'value3',
            'prototype': {
                'key2': {'content': 'value2_1'}
            }
        }
        ret = get_config_value(config, 'key2')

        self.assertEqual(ret, 'value2_1')
