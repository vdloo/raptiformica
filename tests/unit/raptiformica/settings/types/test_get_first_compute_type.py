from raptiformica.settings.types import get_first_compute_type
from tests.testcase import TestCase


class TestGetFirstComputeType(TestCase):
    def setUp(self):
        self.get_first_from_types = self.set_up_patch(
                'raptiformica.settings.types.get_first_from_types'
        )

    def test_get_first_compute_type_gets_first_compute_type(self):
        get_first_compute_type()

        self.get_first_from_types.assert_called_once_with(
            'compute'
        )

    def test_get_first_compute_type_returns_first_compute_type(self):
        ret = get_first_compute_type()

        self.assertEqual(ret, self.get_first_from_types.return_value)

