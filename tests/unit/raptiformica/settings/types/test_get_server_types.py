from raptiformica.settings.types import get_server_types
from tests.testcase import TestCase


class TestGetServerTypes(TestCase):
    def setUp(self):
        self.get_available_types_for_item = self.set_up_patch(
            'raptiformica.settings.types.get_available_types_for_item'
        )

    def test_get_server_types_gets_available_types_for_item(self):
        get_server_types()

        self.get_available_types_for_item.assert_called_once_with('server')

    def test_get_server_types_returns_list_of_server_types(self):
        ret = get_server_types()

        self.assertEqual(ret, self.get_available_types_for_item.return_value)
