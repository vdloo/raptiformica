from urllib.error import URLError

from raptiformica.settings.load import get_config_mapping
from tests.testcase import TestCase


class TestGetConfigMapping(TestCase):
    def setUp(self):
        self.sync_shared_config_mapping = self.set_up_patch(
            'raptiformica.settings.load.sync_shared_config_mapping'
        )
        self.log = self.set_up_patch(
            'raptiformica.settings.load.log'
        )
        self.get_local_config = self.set_up_patch(
            'raptiformica.settings.load.get_local_config_mapping'
        )

    def test_get_config_mapping_syncs_shared_config_mapping(self):
        get_config_mapping()

        self.sync_shared_config_mapping.assert_called_once_with()

    def test_get_config_mapping_returns_synced_shared_config_mapping(self):
        ret = get_config_mapping()

        self.assertEqual(self.sync_shared_config_mapping.return_value, ret)

    def test_get_config_mapping_logs_debug_message_if_the_shared_config_can_not_be_retrieved(self):
        self.sync_shared_config_mapping.side_effect = URLError('reason')

        get_config_mapping()

        self.assertTrue(self.log.debug.called)

    def test_get_config_mapping_gets_local_config_if_the_shared_config_can_not_be_retrieved(self):
        self.sync_shared_config_mapping.side_effect = URLError('reason')

        get_config_mapping()

        self.get_local_config.assert_called_once_with()

    def test_get_config_mapping_returns_local_config_if_the_shared_config_can_not_be_retrieved(self):
        self.sync_shared_config_mapping.side_effect = URLError('reason')

        ret = get_config_mapping()

        self.assertEqual(self.get_local_config.return_value, ret)
