from collections import OrderedDict
from mock import ANY, call

from raptiformica.settings.load import upload_config_mapping
from tests.testcase import TestCase


class TestUploadConfigMapping(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.settings.load.log')
        self.mapping = {
            'some_key': 'some_value',
            'some/other/key': 'some_other_value'
        }
        self.put_mapping = self.set_up_patch('raptiformica.settings.load.consul_conn.put_mapping')

    def test_upload_config_mapping_logs_debug_message(self):
        upload_config_mapping(self.mapping)

        self.assertTrue(self.log.debug.called)

    def test_upload_config_mapping_puts_mapping(self):
        upload_config_mapping(self.mapping)

        self.put_mapping.assert_called_once_with(self.mapping)

    def test_upload_config_mapping_batches_large_mappings(self):
        large_mapping = OrderedDict(('key_{}'.format(name), 'bla') for name in range(128))

        upload_config_mapping(large_mapping)

        expected_calls = (
            call(OrderedDict(('key_{}'.format(name), 'bla') for name in range(32))),
            call(OrderedDict(('key_{}'.format(name), 'bla') for name in range(32, 64))),
            call(OrderedDict(('key_{}'.format(name), 'bla') for name in range(64, 96))),
            call(OrderedDict(('key_{}'.format(name), 'bla') for name in range(96, 128)))
        )
        self.put_mapping.assert_has_calls(expected_calls)

    def test_upload_config_mapping_uses_try_config_config_wrapper(self):
        try_config_request = self.set_up_patch(
            'raptiformica.settings.load.try_config_request'
        )

        upload_config_mapping(self.mapping)

        try_config_request.assert_called_once_with(ANY)
