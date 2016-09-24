from mock import call

from raptiformica.settings.load import load_module_config
from tests.testcase import TestCase


class TestLoadModuleConfig(TestCase):
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
        self.load_json.return_value = {'raptiformica_api_version': '0.1'}
        self.log = self.set_up_patch('raptiformica.settings.load.log')

    def test_load_module_config_lists_all_files_with_extension_in_directory(self):
        list(load_module_config(modules_dir='/tmp/some/directory'))

        self.list_all_files_with_extension_in_directory.assert_called_once_with(
            '/tmp/some/directory', 'json'
        )

    def test_load_configs_json_loads_all_module_configs(self):
        list(load_module_config(modules_dir='/tmp/some/directory'))

        expected_calls = map(call, self.files)
        self.assertCountEqual(self.load_json.mock_calls, expected_calls)

    def test_load_configs_ignores_configs_that_fail_to_load(self):
        self.load_json.side_effect = [
            {'raptiformica_api_version': '0.1'},
            ValueError,
            {'raptiformica_api_version': '0.1'}
        ]

        ret = list(load_module_config(modules_dir='/tmp/some/directory'))

        expected_configs = [{'raptiformica_api_version': '0.1'}] * 2
        self.assertCountEqual(ret, expected_configs)

    def test_load_configs_logs_debug_for_configs_that_fail_to_load(self):
        self.load_json.side_effect = [
            ValueError,
            {'raptiformica_api_version': '0.1'},
            ValueError
        ]

        list(load_module_config(modules_dir='/tmp/some/directory'))

        expected_calls = map(call, (
            'Loading module config from /tmp/some/directory/file1.json',
            'Loading module config from /tmp/some/directory/file2.json',
            'Loading module config from /tmp/some/directory/file3.json',
            'Failed to parse module config in /tmp/some/directory/file1.json, skipping..',
            'Failed to parse module config in /tmp/some/directory/file3.json, skipping..'
        ))
        self.assertCountEqual(self.log.debug.mock_calls, expected_calls)

    def test_load_configs_logs_debug_for_json_files_that_are_not_raptiformica_configs(self):
        self.load_json.side_effect = [
            {}, {'raptiformica_api_version': '0.1'}, {}
        ]

        list(load_module_config(modules_dir='/tmp/some/directory'))

        expected_calls = map(call, (
            'Loading module config from /tmp/some/directory/file1.json',
            'Loading module config from /tmp/some/directory/file2.json',
            'Loading module config from /tmp/some/directory/file3.json',
            'Failed to parse module config in /tmp/some/directory/file1.json, skipping..',
            'Failed to parse module config in /tmp/some/directory/file3.json, skipping..'
        ))
        self.assertCountEqual(self.log.debug.mock_calls, expected_calls)
