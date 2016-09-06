from mock import Mock
from urllib.error import HTTPError

from raptiformica.settings.load import sync_shared_config_mapping
from tests.testcase import TestCase


class TestSyncSharedConfigMapping(TestCase):
    def setUp(self):
        self.download_config = self.set_up_patch(
            'raptiformica.settings.load.download_config'
        )
        self.get_local_config = self.set_up_patch(
            'raptiformica.settings.load.get_local_config'
        )
        self.update_config = self.set_up_patch(
            'raptiformica.settings.load.update_config'
        )
        self.cache_config = self.set_up_patch(
            'raptiformica.settings.load.cache_config'
        )

    def test_sync_shared_config_mapping_downloads_config(self):
        sync_shared_config_mapping()

        self.download_config.assert_called_once_with()

    def test_sync_shared_config_mapping_gets_local_config_if_no_shared_config_yet(self):
        self.download_config.side_effect = HTTPError('url', 'code', 'msg', 'hdrs', Mock())

        sync_shared_config_mapping()

        self.get_local_config.assert_called_once_with()

    def test_sync_shared_config_mapping_uploads_local_config(self):
        self.download_config.side_effect = HTTPError('url', 'code', 'msg', 'hdrs', Mock())

        sync_shared_config_mapping()

        self.update_config.assert_called_once_with(
            self.get_local_config.return_value
        )

    def test_sync_shared_config_caches_downloaded_config(self):
        sync_shared_config_mapping()

        self.cache_config.assert_called_once_with(
            self.download_config.return_value
        )

    def test_sync_shared_config_caches_local_config_if_no_shared_config_yet(self):
        self.download_config.side_effect = HTTPError('url', 'code', 'msg', 'hdrs', Mock())

        sync_shared_config_mapping()

        self.cache_config.assert_called_once_with(
            self.update_config.return_value
        )

    def test_sync_shared_config_returns_shared_config(self):
        ret = sync_shared_config_mapping()

        self.assertEqual(
            self.download_config.return_value, ret
        )

    def test_sync_shared_config_returns_local_config_if_no_shared_config_yet(self):
        self.download_config.side_effect = HTTPError('url', 'code', 'msg', 'hdrs', Mock())

        ret = sync_shared_config_mapping()

        self.assertEqual(
            self.update_config.return_value, ret
        )
