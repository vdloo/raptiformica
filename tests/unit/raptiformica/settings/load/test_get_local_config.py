from raptiformica.settings.load import get_local_config_mapping
from tests.testcase import TestCase


class TestGetLocalConfig(TestCase):
    def setUp(self):
        self.cached_config = self.set_up_patch(
            'raptiformica.settings.load.cached_config_mapping'
        )
        self.log = self.set_up_patch('raptiformica.settings.load.log')
        self.on_disk_mapping = self.set_up_patch(
            'raptiformica.settings.load.on_disk_mapping'
        )

    def test_get_local_config_gets_cached_config(self):
        get_local_config_mapping()

        self.cached_config.assert_called_once_with()

    def test_get_local_config_returns_cached_config(self):
        ret = get_local_config_mapping()

        self.assertEqual(self.cached_config.return_value, ret)

    def test_get_local_config_logs_debug_message_if_cache_not_found(self):
        self.cached_config.side_effect = FileNotFoundError

        get_local_config_mapping()

        self.assertTrue(self.log.debug.called)

    def test_get_local_config_gets_on_disk_mapping_if_cache_not_found(self):
        self.cached_config.side_effect = FileNotFoundError

        get_local_config_mapping()

        self.on_disk_mapping.assert_called_once_with()

    def test_get_local_config_returns_on_disk_mapping_if_cache_not_found(self):
        self.cached_config.side_effect = FileNotFoundError

        ret = get_local_config_mapping()

        self.assertEqual(self.on_disk_mapping.return_value, ret)
