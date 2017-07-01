import socket
from mock import Mock

from consul_kv.api import put_kv
from tests.testcase import TestCase


class TestPutKV(TestCase):
    def setUp(self):
        self.request = self.set_up_patch('consul_kv.api.request')
        self.request.urlopen.return_value.__exit__ = lambda a, b, c, d: None
        self.request.urlopen.return_value.__enter__ = lambda x: Mock()
        self.log = self.set_up_patch('consul_kv.api.log')

    def test_put_kv_instantiates_request_object(self):
        put_kv('some_key', 'some_value')

        self.request.Request.assert_called_once_with(
            url='http://localhost:8500/v1/kv/some_key',
            data=str.encode('some_value'),
            method='PUT'
        )

    def test_put_kv_instantiates_request_object_with_specified_endpoint(self):
        put_kv('some_key', 'some_value', endpoint='http://some_host:8500/v1/kv/')

        self.request.Request.assert_called_once_with(
            url='http://some_host:8500/v1/kv/some_key',
            data=str.encode('some_value'),
            method='PUT'
        )

    def test_put_kv_does_request(self):
        put_kv('some_key', 'some_value')

        self.request.urlopen.assert_called_once_with(
            self.request.Request.return_value,
            timeout=socket._GLOBAL_DEFAULT_TIMEOUT
        )

    def test_put_kv_does_request_with_specified_timeout(self):
        put_kv('some_key', 'some_value', timeout=10)

        self.request.urlopen.assert_called_once_with(
            self.request.Request.return_value,
            timeout=10
        )

    def test_put_kv_logs_debug_message(self):
        put_kv('some_key', 'some_value')

        self.assertTrue(self.log.debug.called)

    def test_put_kv_does_request_with_cas_version_number_as_query_param(self):
        put_kv('some_key', 'some_value', cas=127)

        self.request.Request.assert_called_once_with(
            url='http://localhost:8500/v1/kv/some_key/?cas=127',
            data=str.encode('some_value'),
            method='PUT'
        )
