from raptiformica.settings.load import write_config_mapping
from tests.testcase import TestCase


class TestWriteConfigMapping(TestCase):
    def setUp(self):
        self.write_json = self.set_up_patch(
            'raptiformica.settings.load.write_json'
        )
        self.config_cache_lock = self.set_up_patch(
            'raptiformica.settings.load.config_cache_lock'
        )
        self.config_cache_lock.return_value.__exit__ = lambda a, b, c, d: None
        self.config_cache_lock.return_value.__enter__ = lambda a: None
        self.data = {
            'the': 'data'
        }

    def test_write_config_gets_config_cache_lock(self):
        write_config_mapping(self.data, 'a_config_file.json')

        self.config_cache_lock.assert_called_once_with()

    def test_write_config_writes_json(self):
        write_config_mapping(self.data, 'a_config_file.json')

        self.write_json.assert_called_once_with(
            self.data,
            'a_config_file.json'
        )
