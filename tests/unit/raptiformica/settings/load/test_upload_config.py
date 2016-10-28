from raptiformica.settings.load import upload_config_mapping
from tests.testcase import TestCase


class TestUploadConfig(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.settings.load.log')
        self.mapping = {
            'some_key': 'some_value',
            'some/other/key': 'some_other_value'
        }
        self.put_mapping = self.set_up_patch('raptiformica.settings.load.consul_conn.put_mapping')

    def test_upload_config_logs_debug_message(self):
        upload_config_mapping(self.mapping)

        self.assertTrue(self.log.debug.called)

    def test_upload_config_puts_mapping(self):
        upload_config_mapping(self.mapping)

        self.put_mapping.assert_called_once_with(self.mapping)
