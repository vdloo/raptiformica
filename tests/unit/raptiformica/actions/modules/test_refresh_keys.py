from raptiformica.actions.modules import refresh_keys
from tests.testcase import TestCase


class TestRefreshKeys(TestCase):
    def setUp(self):
        self.new_mapping = {
            'some_key': 'some_value',
            'some/other/key': 'some_other_value',
            'some/other/key2': 'some_other_value2'
        }
        self.old_mapping = {
            'some_key': 'some_old_value',
            'some/other/key': 'some_other_old_value',
            'some_key_that_was/not_overwritten': 'value9'
        }
        self.on_disk_mapping = self.set_up_patch(
            'raptiformica.actions.modules.on_disk_mapping',
            return_value=self.new_mapping
        )
        self.try_update_config = self.set_up_patch(
            'raptiformica.actions.modules.try_update_config'
        )

    def test_refresh_keys_gets_on_disk_mapping(self):
        refresh_keys(self.old_mapping)

        self.on_disk_mapping.assert_called_once_with()

    def test_refresh_keys_only_updates_previously_overwritten_keys(self):
        refresh_keys(self.old_mapping)

        expected_mapping = {
            'some/other/key': 'some_other_value',
            'some_key': 'some_value'
        }
        self.try_update_config.assert_called_once_with(
            expected_mapping
        )
