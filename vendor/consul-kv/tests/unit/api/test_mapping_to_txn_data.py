from base64 import b64encode
from collections import OrderedDict

from consul_kv.api import _mapping_to_txn_data
from tests.testcase import TestCase


class TestMappingToTxnData(TestCase):
    def setUp(self):
        self.mapping = OrderedDict([
            ('some/key/1', 'some_value_1'),
            ('some/key/2', 'some_value_2')
        ])
        self.value_fixture1 = 'c29tZV92YWx1ZV8x'
        self.value_fixture2 = 'c29tZV92YWx1ZV8y'

    def test_mapping_txn_data_value_fixtures_are_correctly_encoded(self):
        def encode(value):
            return b64encode(
                value.encode('utf-8')
            ).decode('utf-8')
        encoded_value1, encoded_value2 = tuple(map(encode, self.mapping.values()))

        self.assertEqual(encoded_value1, self.value_fixture1)
        self.assertEqual(encoded_value2, self.value_fixture2)

    def test_mapping_to_txn_data_returns_txn_data_list_of_mapping(self):
        ret = _mapping_to_txn_data(self.mapping)

        expected_txn_data = [
            {'KV': {'Key': 'some/key/1', 'Value': self.value_fixture1, 'Verb': 'set'}},
            {'KV': {'Key': 'some/key/2', 'Value': self.value_fixture2, 'Verb': 'set'}}
        ]
        self.assertCountEqual(ret, expected_txn_data)

    def test_mapping_to_txn_data_can_deal_with_ints(self):
        self.mapping['some/key/3'] = 123

        _mapping_to_txn_data(self.mapping)

    def test_mapping_to_txn_data_returns_txn_data_list_of_mapping_with_specified_operation(self):
        ret = _mapping_to_txn_data(self.mapping, verb='cas')

        expected_txn_data = [
            {'KV': {'Key': 'some/key/1', 'Value': self.value_fixture1, 'Verb': 'cas'}},
            {'KV': {'Key': 'some/key/2', 'Value': self.value_fixture2, 'Verb': 'cas'}}
        ]
        self.assertCountEqual(ret, expected_txn_data)
