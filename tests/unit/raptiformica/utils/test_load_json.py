from mock import Mock, patch

from raptiformica.utils import load_json
from tests.testcase import TestCase


class TestLoadJson(TestCase):
    def setUp(self):
        self.json_data = '{"compute_types": []}'
        self.open = self.set_up_patch('raptiformica.utils.open')
        self.open.return_value.__exit__ = lambda a, b, c, d: None
        self.file_handle = Mock()
        self.file_handle.read.return_value = self.json_data
        self.open.return_value.__enter__ = lambda x: self.file_handle

    def test_load_json_opens_json_file(self):
        load_json('config.json')

        self.open.assert_called_once_with('config.json', 'r')

    def test_load_json_returns_json_data(self):
        ret = load_json('config.json')

        self.assertEqual(ret, {'compute_types': []})
