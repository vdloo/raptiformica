from os.path import join
from raptiformica.actions.modules import unload_module
from raptiformica.settings import conf
from tests.testcase import TestCase


class TestUnloadModule(TestCase):
    def setUp(self):
        self.determine_clone_data = self.set_up_patch(
            'raptiformica.actions.modules.determine_clone_data',
            return_value=('https://github.com/vdloo/puppetfiles', 'puppetfiles')
        )
        self.on_disk_mapping = self.set_up_patch(
            'raptiformica.actions.modules.on_disk_mapping'
        )
        self.remove_keys = self.set_up_patch(
            'raptiformica.actions.modules.remove_keys'
        )
        self.refresh_keys = self.set_up_patch(
            'raptiformica.actions.modules.refresh_keys'
        )

    def test_unload_module_determines_clone_data(self):
        unload_module('vdloo/puppetfiles')

        self.determine_clone_data.assert_called_once_with(
            'vdloo/puppetfiles'
        )

    def test_unload_module_gets_on_disk_mapping_from_module(self):
        unload_module('vdloo/puppetfiles')

        self.on_disk_mapping.assert_called_once_with(
            module_dirs=(join(conf().USER_MODULES_DIR, 'puppetfiles'),)
        )

    def test_unload_module_removes_keys(self):
        unload_module('vdloo/puppetfiles')

        self.remove_keys.assert_called_once_with(
            self.on_disk_mapping.return_value,
            join(conf().USER_MODULES_DIR, 'puppetfiles')
        )

    def test_unload_module_refreshes_keys(self):
        unload_module('vdloo/puppetfiles')

        self.refresh_keys.assert_called_once_with(
            self.on_disk_mapping.return_value
        )
