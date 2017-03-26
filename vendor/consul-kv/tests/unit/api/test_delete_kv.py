import socket
from mock import Mock

from consul_kv.api import delete_kv
from tests.testcase import TestCase


class TestDeleteKV(TestCase):
    def setUp(self):
        self.request = self.set_up_patch('consul_kv.api.request')
        self.request.urlopen.return_value.__exit__ = lambda a, b, c, d: None
        self.request.urlopen.return_value.__enter__ = lambda x: Mock()
        self.log = self.set_up_patch('consul_kv.api.log')

    def test_delete_kv_instantiates_request_object(self):
        delete_kv('some/path')

        self.request.Request.assert_called_once_with(
            url='http://localhost:8500/v1/kv/some/path',
            method='DELETE'
        )

    def test_delete_kv_instantiates_request_object_with_specified_endpoint(self):
        delete_kv('some/path', endpoint='http://some_host:8500/v1/kv/')

        self.request.Request.assert_called_once_with(
            url='http://some_host:8500/v1/kv/some/path',
            method='DELETE'
        )

    def test_delete_kv_deletes_all_nested_values_if_specified(self):
        delete_kv('some/path', recurse=True)

        self.request.Request.assert_called_once_with(
            url='http://localhost:8500/v1/kv/some/path/?recurse',
            method='DELETE'
        )

    def test_delete_kv_deletes_endpoint_root_if_no_key_specified(self):
        delete_kv()

        self.request.Request.assert_called_once_with(
            url='http://localhost:8500/v1/kv/',
            method='DELETE'
        )

    def test_delete_kv_does_request(self):
        delete_kv('some/path')

        self.request.urlopen.assert_called_once_with(
            self.request.Request.return_value,
            timeout=socket._GLOBAL_DEFAULT_TIMEOUT
        )

    def test_delete_kv_does_request_with_specified_timeout(self):
        delete_kv('some/path', timeout=10)

        self.request.urlopen.assert_called_once_with(
            self.request.Request.return_value,
            timeout=10
        )

    def test_delete_kv_logs_debug_message(self):
        delete_kv('some/path')

        self.assertTrue(self.log.debug)

