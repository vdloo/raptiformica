from mock import call

from raptiformica.actions.modules import remove_keys
from tests.testcase import TestCase


class TestRemoveKeys(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.actions.modules.log'
        )
        self.mapping = {
            'some_key': 'some_value',
            'some_other/key': 'some_other_value'
        }
        self.try_delete_config = self.set_up_patch(
            'raptiformica.actions.modules.try_delete_config'
        )
        self.rmtree = self.set_up_patch(
            'raptiformica.actions.modules.rmtree'
        )

    def test_remove_keys_logs_debug_messages(self):
        remove_keys(self.mapping, '~/.raptiformica/modules/puppetfiles')

        self.assertEqual(2, self.log.debug.call_count)

    def test_remove_keys_deletes_all_keys_from_mapping(self):
        remove_keys(self.mapping, '~/.raptiformica/modules/puppetfiles')

        expected_calls = map(call, self.mapping.keys())
        self.assertCountEqual(
            self.try_delete_config.mock_calls, expected_calls
        )

    def test_remove_keys_removes_module_directory(self):
        remove_keys(self.mapping, '~/.raptiformica/modules/puppetfiles')

        self.rmtree.assert_called_once_with(
            '~/.raptiformica/modules/puppetfiles',
            ignore_errors=True
        )
