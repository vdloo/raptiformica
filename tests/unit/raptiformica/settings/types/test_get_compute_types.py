from raptiformica.settings.types import get_compute_types
from tests.testcase import TestCase


class TestGetComputeTypes(TestCase):
    def setUp(self):
        self.get_available_types_for_item = self.set_up_patch(
            'raptiformica.settings.types.get_available_types_for_item'
        )

    def test_get_compute_types_gets_available_types_for_item(self):
        get_compute_types()

        self.get_available_types_for_item.assert_called_once_with('compute')

    def test_get_compute_types_returns_list_of_compute_types(self):
        ret = get_compute_types()

        self.assertEqual(ret, self.get_available_types_for_item.return_value)

