from raptiformica.settings.types import get_first_server_type
from tests.testcase import TestCase


class TestGetFirstServerType(TestCase):
    def setUp(self):
        self.load_config = self.set_up_patch('raptiformica.settings.types.load_config')
        self.server_types = {'server_types': {'headless': {}, 'workstation': {}}}
        self.load_config.return_value = self.server_types

    def test_get_first_server_type_raises_value_error_if_no_of_that_type_is_configured(self):
        self.load_config.return_value = {'server_types': {}}

        with self.assertRaises(ValueError):
            get_first_server_type()

    def test_get_first_server_type_returns_first_server_type(self):
        ret = get_first_server_type()

        self.assertEqual(ret, 'headless')
