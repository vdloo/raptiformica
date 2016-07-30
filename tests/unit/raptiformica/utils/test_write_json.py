from mock import Mock
from raptiformica.utils import write_json

from tests.testcase import TestCase


class TestWriteJson(TestCase):
    def setUp(self):
        self.json_data = {"compute_types": []}
        self.open = self.set_up_patch('raptiformica.utils.open')
        self.open.return_value.__exit__ = lambda a, b, c, d: None
        self.file_handle = Mock()
        self.open.return_value.__enter__ = lambda x: self.file_handle
        self.json = self.set_up_patch('raptiformica.utils.json')

    def test_write_json_writes_json_to_file(self):
        write_json(self.json_data, 'config.json')

        self.json.dump.assert_called_once_with(
            self.json_data, self.file_handle,
            indent=4, sort_keys=True
        )
