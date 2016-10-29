from mock import ANY

from raptiformica.settings import KEY_VALUE_PATH
from raptiformica.settings.load import download_config_mapping
from tests.testcase import TestCase


class TestDownloadConfigMapping(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.settings.load.log')
        self.get_mapping = self.set_up_patch('raptiformica.settings.load.consul_conn.get_mapping')

    def test_download_config_mapping_logs_debug_message(self):
        download_config_mapping()

        self.assertTrue(self.log.debug.called)

    def test_download_config_mapping_gets_root_kv_mapping(self):
        download_config_mapping()

        self.get_mapping.assert_called_once_with(
            KEY_VALUE_PATH
        )

    def test_download_config_mapping_returns_mapping(self):
        ret = download_config_mapping()

        self.assertEqual(self.get_mapping.return_value, ret)

    def test_download_config_mapping_uses_try_config_config_wrapper(self):
        try_config_request = self.set_up_patch(
            'raptiformica.settings.load.try_config_request'
        )

        download_config_mapping()

        try_config_request.assert_called_once_with(ANY)
