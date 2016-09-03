from raptiformica.settings.types import get_first_server_type
from tests.testcase import TestCase


class TestGetFirstServerType(TestCase):
    def setUp(self):
        self.get_first_from_types = self.set_up_patch(
            'raptiformica.settings.types.get_first_from_types'
        )

    def test_get_first_server_type_gets_first_server_type(self):
        get_first_server_type()

        self.get_first_from_types.assert_called_once_with(
            'server'
        )

    def test_get_first_server_type_returns_first_server_type(self):
        ret = get_first_server_type()

        self.assertEqual(ret, self.get_first_from_types.return_value)
