from raptiformica.settings.server import get_server_types
from tests.testcase import TestCase


class TestGetServerTypes(TestCase):
    def setUp(self):
        self.load_config = self.set_up_patch('raptiformica.settings.server.load_config')
        self.server_types = {'server_types': {'headless': {}, 'workstation': {}}}
        self.load_config.return_value = self.server_types

    def test_get_server_types_loads_config(self):
        get_server_types()

        self.load_config.assert_called_once_with()

    def test_get_server_types_returns_list_of_server_types(self):
        ret = get_server_types()

        self.assertCountEqual(ret, ['headless', 'workstation'])

    def test_get_server_types_returns_empty_list_if_no_server_types(self):
        self.load_config.return_value = {}

        ret = get_server_types()

        self.assertCountEqual(ret, [])
