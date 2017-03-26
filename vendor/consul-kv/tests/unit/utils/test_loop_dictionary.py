from mock import call, Mock

from consul_kv.utils import loop_dictionary
from tests.testcase import TestCase


class TestLoopDictionary(TestCase):
    def setUp(self):
        self.callback = Mock()
        self.dictionary = {
            'some': {'key': 'and', 'some': 'values'},
            'with': {
                'some': {'other': 'keys'},
                'and': {'some': 'other', 'values': 1}
            },
        }

    def test_loop_dictionary_calls_callback_for_all_items_recursively(self):
        loop_dictionary(self.dictionary, callback=self.callback)

        expected_calls = (
            call('with/and', 'values', 1),
            call('with/and', 'some', 'other'),
            call('with/some', 'other', 'keys'),
            call('some', 'key', 'and'),
            call('some', 'some', 'values')
        )
        self.assertCountEqual(self.callback.mock_calls, expected_calls)

    def test_loop_dictionary_calls_callback_for_all_items_recursively_with_specified_path(self):
        loop_dictionary(self.dictionary, path='/some/endpoint', callback=self.callback)

        expected_calls = (
            call('/some/endpoint/with/and', 'values', 1),
            call('/some/endpoint/with/and', 'some', 'other'),
            call('/some/endpoint/with/some', 'other', 'keys'),
            call('/some/endpoint/some', 'key', 'and'),
            call('/some/endpoint/some', 'some', 'values')
        )
        self.assertCountEqual(self.callback.mock_calls, expected_calls)
