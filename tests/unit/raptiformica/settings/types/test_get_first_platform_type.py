from raptiformica.settings.types import get_first_platform_type
from tests.testcase import TestCase


class TestGetFirstPlatformType(TestCase):
    def setUp(self):
        self.get_first_from_types = self.set_up_patch(
            'raptiformica.settings.types.get_first_from_types'
        )

    def test_get_first_platform_type_gets_first_platform_type(self):
        get_first_platform_type()

        self.get_first_from_types.assert_called_once_with(
            'platform'
        )

    def test_get_first_platform_type_returns_first_platform_type(self):
        ret = get_first_platform_type()

        self.assertEqual(ret, self.get_first_from_types.return_value)
