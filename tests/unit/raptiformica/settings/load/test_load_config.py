from mock import call

from raptiformica.settings import BASE_CONFIG, MODULES_DIR
from raptiformica.settings.load import load_config
from tests.testcase import TestCase


class TestLoadConfig(TestCase):
    def setUp(self):
        self.load_json = self.set_up_patch('raptiformica.settings.load.load_json')
        self.data = {'compute_types': []}
        self.load_json.return_value = self.data
        self.load_modules = self.set_up_patch('raptiformica.settings.load.load_modules')
        self.load_modules.return_value = {'compute_types': {}}
        self.write_config = self.set_up_patch('raptiformica.settings.load.write_config')

    def test_load_config_loads_json(self):
        ret = load_config(config_file='myconfig.json')

        self.load_json.assert_called_once_with('myconfig.json')
        self.assertEqual(ret, self.data)

    def test_load_config_loads_base_config_if_no_such_file(self):
        self.load_json.side_effect = OSError

        ret = load_config(config_file='myconfig.json')

        self.load_json.assert_called_once_with('myconfig.json')
        self.load_modules.assert_called_once_with(modules_dir=MODULES_DIR)
        self.assertEqual(ret, self.load_modules.return_value)

    def test_load_config_loads_base_config_if_config_file_can_not_be_parsed(self):
        self.load_json.side_effect = (ValueError, self.data)

        ret = load_config(config_file='myconfig.json')

        self.load_json.assert_called_once_with('myconfig.json')
        self.load_modules.assert_called_once_with(modules_dir=MODULES_DIR)
        self.assertEqual(ret, self.load_modules.return_value)

    def test_load_config_writes_base_config_if_config_file_can_not_be_parsed(self):
        self.load_json.side_effect = (ValueError, self.data)

        load_config(config_file='myconfig.json')

        self.write_config.assert_called_once_with(self.load_modules.return_value, 'myconfig.json')

    def test_load_config_errors_out_if_base_config_is_also_invalid(self):
        self.load_json.side_effect = OSError
        self.load_modules.return_value = {}

        with self.assertRaises(ValueError):
            load_config(config_file='myconfig.json')
