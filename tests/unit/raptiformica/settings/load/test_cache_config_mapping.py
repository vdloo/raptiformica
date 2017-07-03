from raptiformica.settings import conf
from raptiformica.settings.load import cache_config_mapping
from tests.testcase import TestCase


class TestCacheConfigMapping(TestCase):
    def setUp(self):
        self.mapping = {
            'some/key': 'some_value',
            'some/other/key1': 'some_other_value1'
        }
        self.write_config = self.set_up_patch(
            'raptiformica.settings.load.write_config_mapping'
        )
        self.validate_config_mapping = self.set_up_patch(
            'raptiformica.settings.load.validate_config_mapping'
        )
        self.validate_config_mapping.return_value = True

    def test_cache_config_mapping_raises_error_if_empty_mapping(self):
        with self.assertRaises(RuntimeError):
            cache_config_mapping({})

    def test_cache_config_mapping_raises_error_if_invalid_mapping(self):
        self.validate_config_mapping.return_value = False

        with self.assertRaises(RuntimeError):
            cache_config_mapping(self.mapping)

    def test_cache_config_mapping_writes_mapping_to_mutable_config(self):
        cache_config_mapping(self.mapping)

        self.write_config.assert_called_once_with(
            self.mapping,
            conf().MUTABLE_CONFIG
        )

