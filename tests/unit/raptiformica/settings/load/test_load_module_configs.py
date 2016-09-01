from mock import call

from raptiformica.settings.load import load_module_configs
from tests.testcase import TestCase


class TestLoadModuleConfigs(TestCase):
    def setUp(self):
        self.list_all_files_with_extension_in_directory = self.set_up_patch(
            'raptiformica.settings.load.list_all_files_with_extension_in_directory'
        )
        self.files = [
            '/tmp/some/directory/file1.json',
            '/tmp/some/directory/file2.json',
            '/tmp/some/directory/file3.json'
        ]
        self.list_all_files_with_extension_in_directory.return_value = self.files
        self.load_json = self.set_up_patch('raptiformica.settings.load.load_json')
        self.log = self.set_up_patch('raptiformica.settings.load.log')

    def test_load_module_configs_lists_all_files_with_extension_in_directory(self):
        list(load_module_configs(modules_dir='/tmp/some/directory'))

        self.list_all_files_with_extension_in_directory.assert_called_once_with(
            '/tmp/some/directory', 'json'
        )

    def test_load_configs_json_loads_all_module_configs(self):
        list(load_module_configs(modules_dir='/tmp/some/directory'))

        expected_calls = map(call, self.files)
        self.assertCountEqual(self.load_json.mock_calls, expected_calls)

    def test_load_configs_ignores_configs_that_fail_to_load(self):
        self.load_json.side_effect = [{}, ValueError, {}]

        ret = list(load_module_configs(modules_dir='/tmp/some/directory'))

        expected_configs = [{}] * 2
        self.assertCountEqual(ret, expected_configs)

    def test_load_configs_logs_warning_for_configs_that_fail_to_load(self):
        self.load_json.side_effect = [ValueError, {}, ValueError]

        list(load_module_configs(modules_dir='/tmp/some/directory'))

        expected_calls = map(call, (
            'Failed to parse module config in /tmp/some/directory/file1.json, skipping..',
            'Failed to parse module config in /tmp/some/directory/file3.json, skipping..'
        ))
        self.assertCountEqual(self.log.warning.mock_calls, expected_calls)
