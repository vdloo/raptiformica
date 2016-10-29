from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.load import purge_local_config_mapping
from tests.testcase import TestCase


class TestPurgeLocalConfigMapping(TestCase):
    def setUp(self):
        self.remove = self.set_up_patch(
            'raptiformica.settings.load.remove'
        )

    def test_purge_local_config_mapping_removes_mutable_config(self):
        purge_local_config_mapping()

        self.remove.assert_called_once_with(MUTABLE_CONFIG)

    def test_purge_local_config_mapping_ignores_file_not_found(self):
        self.remove.side_effect = FileNotFoundError

        # Does not raise error
        purge_local_config_mapping()
