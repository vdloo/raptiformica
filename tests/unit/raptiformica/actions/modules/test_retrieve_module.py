from os.path import join

from raptiformica.actions.modules import retrieve_module
from raptiformica.settings import USER_MODULES_DIR
from tests.testcase import TestCase


class TestRetrieveModule(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
                'raptiformica.actions.modules.log'
        )
        self.determine_clone_data = self.set_up_patch(
            'raptiformica.actions.modules.determine_clone_data',
            return_value=(
                'https://github.com/vdloo/puppetfiles',
                'puppetfiles'
            )
        )
        self.clone_source = self.set_up_patch(
            'raptiformica.actions.modules.clone_source'
        )

    def test_retrieve_module_logs_info_message(self):
        retrieve_module('vdloo/puppetfiles')

        self.assertTrue(self.log.info.called)

    def test_retrieve_module_determines_clone_data_for_module(self):
        retrieve_module('vdloo/puppetfiles')

        self.determine_clone_data.assert_called_once_with(
            'vdloo/puppetfiles'
        )

    def test_retrieve_module_logs_debug_message(self):
        retrieve_module('vdloo/puppetfiles')

        self.assertTrue(self.log.debug.called)

    def test_retrieve_module_clones_source_to_user_modules_dir(self):
        retrieve_module('vdloo/puppetfiles')

        self.clone_source.assert_called_once_with(
            'https://github.com/vdloo/puppetfiles',
            join(USER_MODULES_DIR, 'puppetfiles')
        )
