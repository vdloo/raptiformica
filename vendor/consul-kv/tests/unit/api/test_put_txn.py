import socket
import json

from mock import Mock

from consul_kv.api import _mapping_to_txn_data
from tests.testcase import TestCase

from consul_kv import put_kv_txn


class TestPutTxn(TestCase):
    def setUp(self):
        self.request = self.set_up_patch('consul_kv.api.request')
        self.request.urlopen.return_value.__exit__ = lambda a, b, c, d: None
        self.request.urlopen.return_value.__enter__ = lambda x: Mock()
        self.log = self.set_up_patch('consul_kv.api.log')
        self.mapping = {
            'some/key/1': 'some_value_1',
            'some/key/2': 'some_value_2'
        }
        self.expected_data = json.dumps(
            _mapping_to_txn_data(self.mapping, verb='set')
        ).encode('utf-8')

    def test_put_kv_txn_instantiates_request_object(self):
        put_kv_txn(self.mapping)

        self.request.Request.assert_called_once_with(
            url='http://localhost:8500/v1/txn/',
            data=self.expected_data,
            method='PUT',
            headers={'Content-Type': 'application/json'}
        )

    def test_put_kv_txn_instantiates_request_object_with_specified_endpoint(self):
        put_kv_txn(self.mapping, endpoint='http://some_host:8500/v1/txn/')

        self.request.Request.assert_called_once_with(
            url='http://some_host:8500/v1/txn/',
            data=self.expected_data,
            method='PUT',
            headers={'Content-Type': 'application/json'}
        )

    def test_put_kv_txn_does_request(self):
        put_kv_txn(self.mapping)

        self.request.urlopen.assert_called_once_with(
            self.request.Request.return_value,
            timeout=socket._GLOBAL_DEFAULT_TIMEOUT
        )

    def test_put_kv_txn_does_request_with_specified_timeout(self):
        put_kv_txn(self.mapping, timeout=10)

        self.request.urlopen.assert_called_once_with(
            self.request.Request.return_value,
            timeout=10
        )

    def test_put_kv_txn_logs_debug_message(self):
        put_kv_txn(self.mapping)

        self.assertTrue(self.log.debug.called)
