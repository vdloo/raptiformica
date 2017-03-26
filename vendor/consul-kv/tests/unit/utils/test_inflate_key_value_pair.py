from consul_kv.utils import inflate_key_value_pair
from tests.testcase import TestCase


class TestInflateKeyValuePair(TestCase):
    def test_inflate_key_value_pair_inflates_key_value_pair(self):
        ret = inflate_key_value_pair('some/key', 'value')

        expected_dictionary = {
            'some': {'key': 'value'}
        }
        self.assertEqual(ret, expected_dictionary)