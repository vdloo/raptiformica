from mock import call

from raptiformica.settings import conf
from raptiformica.settings.load import load_module_configs
from tests.testcase import TestCase


class TestLoadModuleConfigs(TestCase):
    def setUp(self):
        self.load_module_config = self.set_up_patch(
            'raptiformica.settings.load.load_module_config'
        )
        self.load_module_config.return_value = [{}]

    def test_load_module_configs_loads_module_configs(self):
        list(load_module_configs())

        expected_calls = map(
            call, (conf().MODULES_DIR, conf().USER_MODULES_DIR)
        )
        self.assertCountEqual(
            self.load_module_config.mock_calls, expected_calls
        )

    def test_load_module_configs_flattens_module_configs(self):
        ret = load_module_configs()

        self.assertCountEqual(ret, [{}] * 2)

