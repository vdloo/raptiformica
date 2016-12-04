from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.load import cached_config_mapping
from tests.testcase import TestCase


class TestCachedConfigMapping(TestCase):
    def setUp(self):
        self.load_json = self.set_up_patch(
            'raptiformica.settings.load.load_json'
        )
        self.config_cache_lock = self.set_up_patch(
            'raptiformica.settings.load.config_cache_lock'
        )
        self.config_cache_lock.return_value.__exit__ = lambda a, b, c, d: None
        self.config_cache_lock.return_value.__enter__ = lambda a: None

    def test_cached_config_gets_config_cache_lock_before_reading_cached_config(self):
        cached_config_mapping()

        self.config_cache_lock.assert_called_once_with()

    def test_cached_config_loads_mutable_config_as_json(self):
        cached_config_mapping()

        self.load_json.assert_called_once_with(MUTABLE_CONFIG)

    def test_cached_config_returns_parsed_mutable_config_as_json(self):
        ret = cached_config_mapping()

        self.assertEqual(self.load_json.return_value, ret)

