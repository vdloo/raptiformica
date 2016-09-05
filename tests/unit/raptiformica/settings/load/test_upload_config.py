from mock import call

from raptiformica.settings import KEY_VALUE_ENDPOINT
from raptiformica.settings.load import upload_config
from tests.testcase import TestCase


class TestUploadConfig(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.settings.load.log')
        self.mapped = {
            'some_key': 'some_value',
            'some/other/key': 'some_other_value'
        }
        self.put_kv = self.set_up_patch('raptiformica.settings.load.put_kv')

    def test_upload_config_logs_debug_message(self):
        upload_config(self.mapped)

        self.assertTrue(self.log.debug.called)

    def test_upload_config_puts_all_key_value_pairs_in_mapping(self):
        upload_config(self.mapped)

        expected_calls = [
            call(KEY_VALUE_ENDPOINT, 'some_key', 'some_value'),
            call(KEY_VALUE_ENDPOINT, 'some/other/key', 'some_other_value'),
        ]
        self.assertCountEqual(
            self.put_kv.mock_calls, expected_calls
        )
