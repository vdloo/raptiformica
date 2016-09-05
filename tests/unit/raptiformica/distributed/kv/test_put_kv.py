from mock import Mock

from raptiformica.distributed.kv import put_kv
from tests.testcase import TestCase


class TestPutKV(TestCase):
    def setUp(self):
        self.request = self.set_up_patch('raptiformica.distributed.kv.request')
        self.request.urlopen.return_value.__exit__ = lambda a, b, c, d: None
        self.request.urlopen.return_value.__enter__ = lambda x: Mock()
        self.log = self.set_up_patch('raptiformica.distributed.kv.log')

    def test_put_kv_instantiates_request_object(self):
        put_kv('some/path', 'some_key', 'some_value')

        self.request.Request.assert_called_once_with(
            url='some/path/some_key',
            data=str.encode('some_value'),
            method='PUT'
        )

    def test_put_kv_does_request(self):
        put_kv('some/path', 'some_key', 'some_value')

        self.request.urlopen.assert_called_once_with(
            self.request.Request.return_value
        )

    def test_put_logs_debug_message(self):
        put_kv('some/path', 'some_key', 'some_value')

        self.assertTrue(self.log.debug.called)
