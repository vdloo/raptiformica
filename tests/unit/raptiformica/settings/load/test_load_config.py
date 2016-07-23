from mock import call

from raptiformica.settings import BASE_CONFIG
from raptiformica.settings.load import load_config
from tests.testcase import TestCase


class TestLoadConfig(TestCase):
    def setUp(self):
        self.load_json = self.set_up_patch('raptiformica.settings.load.load_json')
        self.data = {'compute_types': []}
        self.load_json.return_value = self.data

    def test_load_config_loads_json(self):
        ret = load_config(config_file='myconfig.json')

        self.load_json.assert_called_once_with('myconfig.json')
        self.assertEqual(ret, self.data)

    def test_load_config_loads_base_config_if_no_such_file(self):
        self.load_json.side_effect = (OSError, self.data)

        ret = load_config(config_file='myconfig.json')

        expected_calls = [
            call('myconfig.json'), call(BASE_CONFIG)
        ]
        self.assertEqual(expected_calls, self.load_json.mock_calls)
        self.assertEqual(ret, self.data)

    def test_load_config_loads_base_config_if_config_file_can_not_be_parsed(self):
        self.load_json.side_effect = (ValueError, self.data)

        ret = load_config(config_file='myconfig.json')

        expected_calls = [
            call('myconfig.json'), call(BASE_CONFIG)
        ]
        self.assertEqual(expected_calls, self.load_json.mock_calls)
        self.assertEqual(ret, self.data)

    def test_load_config_errors_out_if_base_config_is_also_invalid(self):
        self.load_json.side_effect = (OSError, ValueError)

        with self.assertRaises(ValueError):
            load_config(config_file='myconfig.json')
