from copy import deepcopy

from consul_kv.utils import dict_merge
from tests.testcase import TestCase


class TestDictMerge(TestCase):
    def setUp(self):
        self.first_dict = {
            'this': {'is': {'a': 1}},
            'dict': {'with': {'some': 'values'}}
        }
        self.second_dict = {
            'this': {'is': {'another': 'dict'}},
            'with': {'some': 'other', 'values': 1}
        }

    def test_dict_merge_merges_two_dicts(self):
        ret = dict_merge(self.first_dict, self.second_dict)

        expected_dictionary = {
            'this': {'is': {'a': 1, 'another': 'dict'}},
            'dict': {'with': {'some': 'values'}},
            'with': {'some': 'other', 'values': 1}
        }
        self.assertEqual(ret, expected_dictionary)

    def test_dict_merge_does_not_mutate_first_dict(self):
        original_dict = deepcopy(self.first_dict)

        dict_merge(self.first_dict, self.second_dict)

        self.assertEqual(original_dict, self.first_dict)

    def test_dict_merge_does_not_mutate_second_dict(self):
        original_dict = deepcopy(self.second_dict)

        dict_merge(self.first_dict, self.second_dict)

        self.assertEqual(original_dict, self.second_dict)

    def test_dict_merge_overwrites_collisions(self):
        self.first_dict['this']['is'] = 'not a dict we can merge'

        ret = dict_merge(self.first_dict, self.second_dict)

        expected_dictionary = {
            # no 'not a dict we can merge' string
            'this': {'is': {'another': 'dict'}},
            'dict': {'with': {'some': 'values'}},
            'with': {'some': 'other', 'values': 1}
        }
        self.assertEqual(ret, expected_dictionary)
