from raptiformica.actions.modules import load_module
from tests.testcase import TestCase


class TestLoadModule(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.actions.modules.log'
        )
        self.unload_module = self.set_up_patch(
            'raptiformica.actions.modules.unload_module'
        )
        self.retrieve_module = self.set_up_patch(
            'raptiformica.actions.modules.retrieve_module'
        )
        self.load_configs = self.set_up_patch(
            'raptiformica.actions.modules.load_configs'
        )

    def test_load_module_logs_debug_message(self):
        load_module('vdloo/puppetfiles')

        self.assertTrue(self.log.debug.called)

    def test_load_module_unloads_module(self):
        load_module('vdloo/puppetfiles')

        self.unload_module.assert_called_once_with(
            'vdloo/puppetfiles'
        )

    def test_load_module_retrieves_module(self):
        load_module('vdloo/puppetfiles')

        self.retrieve_module.assert_called_once_with(
            'vdloo/puppetfiles'
        )

    def test_load_module_loads_configs(self):
        load_module('vdloo/puppetfiles')

        self.load_configs.assert_called_once_with(
            'vdloo/puppetfiles'
        )

