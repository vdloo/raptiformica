from raptiformica.settings.load import write_config_mapping
from tests.testcase import TestCase


class TestWriteConfig(TestCase):
    def setUp(self):
        self.write_json = self.set_up_patch('raptiformica.settings.load.write_json')
        self.data = {
            'the': 'data'
        }

    def test_write_config_writes_json(self):
        write_config_mapping(self.data, 'a_config_file.json')

        self.write_json.assert_called_once_with(
            self.data,
            'a_config_file.json'
        )