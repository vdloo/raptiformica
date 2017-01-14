from os.path import join

from raptiformica.actions.modules import load_configs
from raptiformica.settings import conf
from tests.testcase import TestCase


class TestLoadConfigs(TestCase):
    def setUp(self):
        self.determine_clone_data = self.set_up_patch(
            'raptiformica.actions.modules.determine_clone_data',
            return_value=(
                'https://github.com/vdloo/puppetfiles',
                'puppetfiles'
            )
        )
        self.on_disk_mapping = self.set_up_patch(
            'raptiformica.actions.modules.on_disk_mapping'
        )
        self.log = self.set_up_patch(
            'raptiformica.actions.modules.log'
        )
        self.try_update_config = self.set_up_patch(
            'raptiformica.actions.modules.try_update_config_mapping'
        )

    def test_load_configs_determines_clone_data_from_module_name(self):
        load_configs('vdloo/puppetfiles')

        self.determine_clone_data.assert_called_once_with(
            'vdloo/puppetfiles'
        )

    def test_load_configs_gets_on_disk_mapping(self):
        load_configs('vdloo/puppetfiles')

        self.on_disk_mapping.assert_called_once_with(
            module_dirs=(join(conf().USER_MODULES_DIR, 'puppetfiles'),)
        )

    def test_load_configs_logs_debug_message(self):
        load_configs('vdloo/puppetfiles')

        self.assertTrue(self.log.debug.called)

    def test_load_configs_updates_config_mapping(self):
        load_configs('vdloo/puppetfiles')

        self.try_update_config.assert_called_once_with(
            self.on_disk_mapping.return_value
        )
