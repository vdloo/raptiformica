from consul_kv import dictionary_map
from tests.testcase import TestCase


class TestDictionaryMap(TestCase):
    def setUp(self):
        self.mapping = {
            'some/key': 'and',
            'some/some': 'values',
            'with/and/some': 'other',
            'with/and/values': 1,
            'with/some/other': 'keys'
        }

    def test_dictionary_map_returns_mapping_converted_to_dictionary(self):
        ret = dictionary_map(self.mapping)

        expected_dictionary = {
            'some': {'key': 'and', 'some': 'values'},
            'with': {
                'some': {'other': 'keys'},
                'and': {'some': 'other', 'values': 1}
            },
        }
        self.assertEqual(ret, expected_dictionary)
