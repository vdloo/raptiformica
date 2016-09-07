from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.load import cache_config
from tests.testcase import TestCase


class TestCacheConfig(TestCase):
    def setUp(self):
        self.mapping = {
            'some/key': 'some_value',
            'some/other/key1': 'some_other_value1'
        }
        self.write_config = self.set_up_patch(
            'raptiformica.settings.load.write_config'
        )

    def test_cache_config_raises_error_if_empty_mapping(self):
        with self.assertRaises(RuntimeError):
            cache_config({})

    def test_cache_config_writes_mapping_to_mutable_config(self):
        cache_config(self.mapping)

        self.write_config.assert_called_once_with(
            self.mapping,
            MUTABLE_CONFIG
        )

