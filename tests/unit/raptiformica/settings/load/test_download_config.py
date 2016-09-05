from os.path import join

from raptiformica.settings import KEY_VALUE_ENDPOINT, KEY_VALUE_PATH
from raptiformica.settings.load import download_config
from tests.testcase import TestCase


class TestDownloadConfig(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.settings.load.log')
        self.get_kv = self.set_up_patch('raptiformica.settings.load.get_kv')

    def test_download_config_logs_debug_message(self):
        download_config()

        self.assertTrue(self.log.debug.called)

    def test_download_config_gets_root_kv_mapping(self):
        download_config()

        self.get_kv.assert_called_once_with(
            join(KEY_VALUE_ENDPOINT, KEY_VALUE_PATH),
            recurse=True
        )

    def test_download_config_returns_mapping(self):
        ret = download_config()

        self.assertEqual(self.get_kv.return_value, ret)
