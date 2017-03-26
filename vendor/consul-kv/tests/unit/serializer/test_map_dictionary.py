from consul_kv import map_dictionary
from tests.testcase import TestCase


class TestMapDictionary(TestCase):
    def setUp(self):
        self.dictionary = {
            'some': {'key': 'and', 'some': 'values'},
            'with': {
                'some': {'other': 'keys'},
                'and': {'some': 'other', 'values': 1}
            },
        }

    def test_map_dictionary_returns_mapped_dictionary(self):
        ret = map_dictionary(self.dictionary)

        expected_mapping = {
            'some/key': 'and',
            'some/some': 'values',
            'with/and/some': 'other',
            'with/and/values': 1,
            'with/some/other': 'keys'
        }
        self.assertEqual(ret, expected_mapping)
