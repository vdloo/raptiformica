from raptiformica.settings.types import get_first_from_types
from tests.testcase import TestCase


class TestGetFirstFromTypes(TestCase):
    def setUp(self):
        self.get_available_types_for_item = self.set_up_patch(
            'raptiformica.settings.types.get_available_types_for_item'
        )
        self.get_available_types_for_item.return_value = [
            'headless', 'workstation'
        ]

    def test_get_first_from_types_gets_available_types_for_item(self):
        get_first_from_types('server_types')

        self.get_available_types_for_item.assert_called_once_with(
            'server_types'
        )

    def test_get_first_from_types_exits_when_no_available_type_configured(self):
        self.get_available_types_for_item.return_value = []

        with self.assertRaises(SystemExit):
            get_first_from_types('server_types')

    def test_get_first_from_types_returns_first_type(self):
        ret = get_first_from_types('server_types')

        self.assertEqual(ret, 'headless')
