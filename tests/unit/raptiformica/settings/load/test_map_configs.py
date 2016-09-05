from raptiformica.settings.load import map_configs
from tests.testcase import TestCase


class TestMapConfigs(TestCase):
    def setUp(self):
        self.configs = [
            {'this': {'is': 'a_config'}, 'value': 1},
            {'yet': 'another', 'config': {'value': 2}}
        ]

    def test_map_configs_returns_config_as_flat_mapping(self):
        ret = map_configs(self.configs)

        expected_mapping = {
            'raptiformica/config/value': 2,
            'raptiformica/this/is': 'a_config',
            'raptiformica/value': 1,
            'raptiformica/yet': 'another'
        }
        self.assertEqual(ret, expected_mapping)
