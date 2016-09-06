from mock import Mock

from raptiformica.distributed.kv import delete_kv
from tests.testcase import TestCase


class TestDeleteKV(TestCase):
    def setUp(self):
        self.request = self.set_up_patch('raptiformica.distributed.kv.request')
        self.request.urlopen.return_value.__exit__ = lambda a, b, c, d: None
        self.request.urlopen.return_value.__enter__ = lambda x: Mock()
        self.log = self.set_up_patch('raptiformica.distributed.kv.log')

    def test_delete_kv_instantiates_request_object(self):
        delete_kv('some/path')

        self.request.Request.assert_called_once_with(
            url='some/path',
            method='DELETE'
        )

    def test_delete_kv_deletes_all_nested_values_if_specified(self):
        delete_kv('some/path', recurse=True)

        self.request.Request.assert_called_once_with(
            url='some/path/?recurse',
            method='DELETE'
        )

    def test_delete_kv_does_request(self):
        delete_kv('some/path')

        self.request.urlopen.assert_called_once_with(
            self.request.Request.return_value
        )

    def test_delete_kv_logs_debug_message(self):
        delete_kv('some/path')

        self.assertTrue(self.log.debug)

