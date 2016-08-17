from raptiformica.utils import find_key_in_dict_recursively
from tests.testcase import TestCase


class TestFindKeyInDictRecursively(TestCase):
    def setUp(self):
        self.dictionary = {
            'key': {
                'needle': 'value1'
            },
            'needle': 'value2'
        }

    def test_find_key_in_dict_recursively_finds_keys_in_dict_recursively(self):
        ret = find_key_in_dict_recursively(self.dictionary, 'needle')

        expected_ret = (
            'value1', 'value2'
        )
        self.assertCountEqual(ret, expected_ret)

    def test_find_key_in_dict_recusively_returns_empty_list_if_no_such_key_in_dictionary(self):
        ret = find_key_in_dict_recursively(self.dictionary, 'does_not_exist')

        expected_ret = list()
        self.assertCountEqual(ret, expected_ret)
