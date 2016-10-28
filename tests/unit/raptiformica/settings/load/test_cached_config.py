from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.load import cached_config_mapping
from tests.testcase import TestCase


class TestCachedConfig(TestCase):
    def setUp(self):
        self.load_json = self.set_up_patch(
            'raptiformica.settings.load.load_json'
        )

    def test_cached_config_loads_mutable_config_as_json(self):
        cached_config_mapping()

        self.load_json.assert_called_once_with(MUTABLE_CONFIG)

    def test_cached_config_returns_parsed_mutable_config_as_json(self):
        ret = cached_config_mapping()

        self.assertEqual(self.load_json.return_value, ret)

