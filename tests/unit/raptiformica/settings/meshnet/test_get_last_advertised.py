from raptiformica.settings import conf
from raptiformica.settings.meshnet import get_last_advertised
from tests.testcase import TestCase


class TestGetLastAdvertised(TestCase):
    def setUp(self):
        self.load_json = self.set_up_patch(
            'raptiformica.settings.meshnet.load_json'
        )

    def test_get_last_advertised_loads_last_advertised_json(self):
        get_last_advertised()

        self.load_json.assert_called_once_with(
            conf().LAST_ADVERTISED
        )

    def test_get_last_advertised_returns_last_advertised_json(self):
        ret = get_last_advertised()

        self.assertEqual(ret, self.load_json.return_value)
