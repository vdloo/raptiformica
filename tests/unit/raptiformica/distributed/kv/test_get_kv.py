from mock import Mock

from raptiformica.distributed.kv import get_kv
from tests.testcase import TestCase


class TestGetKV(TestCase):
    def setUp(self):
        self.request = self.set_up_patch('raptiformica.distributed.kv.request')
        self.request.urlopen.return_value.__exit__ = lambda a, b, c, d: None
        self.json_dump = '[{"Key": "key1", "Value": "Value"}]'
        self.base64decode = self.set_up_patch('raptiformica.distributed.kv.b64decode')
        self.base64decode.return_value = 'value1'.encode('utf-8')
        self.request.urlopen.return_value.__enter__ = lambda x: Mock(
            read=lambda: Mock(
                decode=lambda _: self.json_dump
            )
        )

    def test_get_kv_instantiates_request_object(self):
        get_kv('some/path')

        self.request.Request.assert_called_once_with(
            url='some/path',
            method='GET'
        )

    def test_get_kv_gets_all_nested_values_if_specified(self):
        get_kv('some/path', recurse=True)

        self.request.Request.assert_called_once_with(
            url='some/path/?recurse',
            method='GET'
        )

    def test_get_kv_does_request(self):
        get_kv('some/path', recurse=True)

        self.request.urlopen.assert_called_once_with(
            self.request.Request.return_value
        )

    def test_get_kv_returns_mapping(self):
        ret = get_kv('some/path', recurse=True)

        expected_mapping = {
            'key1': 'value1'
        }
        self.assertEqual(ret, expected_mapping)
