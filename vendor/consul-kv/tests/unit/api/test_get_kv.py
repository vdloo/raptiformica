import socket
from mock import Mock

from consul_kv import get_kv
from tests.testcase import TestCase


class TestGetKV(TestCase):
    def setUp(self):
        self.request = self.set_up_patch('consul_kv.api.request')
        self.request.urlopen.return_value.__exit__ = lambda a, b, c, d: None
        self.json_dump = '[{"Key": "key1", "Value": "Value"}]'
        self.base64decode = self.set_up_patch('consul_kv.api.b64decode')
        self.base64decode.return_value = 'value1'.encode('utf-8')
        self.request.urlopen.return_value.__enter__ = lambda x: Mock(
            read=lambda: Mock(
                decode=lambda _: self.json_dump
            )
        )

    def test_get_kv_instantiates_request_object(self):
        get_kv('some/path')

        expected_url = 'http://localhost:8500/v1/kv/some/path'
        self.request.Request.assert_called_once_with(
            url=expected_url,
            method='GET'
        )

    def test_get_kv_instantiates_request_object_with_specified_endpoint(self):
        get_kv('some/path', endpoint='http://some_host:8500/v1/kv/')

        expected_url = 'http://some_host:8500/v1/kv/some/path'
        self.request.Request.assert_called_once_with(
            url=expected_url,
            method='GET'
        )

    def test_get_kv_gets_all_nested_values_if_specified(self):
        get_kv('some/path', recurse=True)

        expected_url = 'http://localhost:8500/v1/kv/some/path/?recurse'
        self.request.Request.assert_called_once_with(
            url=expected_url,
            method='GET'
        )

    def test_kv_gets_endpoint_root_if_no_key_specified(self):
        get_kv()

        expected_url = 'http://localhost:8500/v1/kv/'
        self.request.Request.assert_called_once_with(
            url=expected_url,
            method='GET'
        )

    def test_get_kv_does_request(self):
        get_kv('some/path', recurse=True)

        self.request.urlopen.assert_called_once_with(
            self.request.Request.return_value,
            timeout=socket._GLOBAL_DEFAULT_TIMEOUT
        )

    def test_kv_does_request_with_specified_timeout(self):
        get_kv('some/path', recurse=True, timeout=10)

        self.request.urlopen.assert_called_once_with(
            self.request.Request.return_value,
            timeout=10
        )

    def test_get_kv_returns_mapping(self):
        ret = get_kv('some/path', recurse=True)

        expected_mapping = {
            'key1': 'value1'
        }
        self.assertEqual(ret, expected_mapping)
