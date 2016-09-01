from raptiformica.settings import MODULES_DIR, ABS_CACHE_DIR
from raptiformica.settings.load import load_unresolved_modules
from tests.testcase import TestCase


class TestLoadUnresolvedModules(TestCase):
    def setUp(self):
        self.load_modules = self.set_up_patch(
            'raptiformica.settings.load.load_modules'
        )
        self.load_modules.return_value = {
            'module_prototype': {'a': 'prototype'}
        }
        self.resolve_prototypes = self.set_up_patch(
            'raptiformica.settings.load.resolve_prototypes'
        )
        self.un_resolve_prototypes = self.set_up_patch(
            'raptiformica.settings.load.un_resolve_prototypes'
        )

    def test_load_unresolved_modules_loads_modules(self):
        load_unresolved_modules()

        self.load_modules.assert_called_once_with(
            modules_dirs=(MODULES_DIR, ABS_CACHE_DIR)
        )

    def test_load_unresolved_modules_loads_specified_modules_dir(self):
        load_unresolved_modules(modules_dirs=('/tmp/modules/dir', '/tmp/a/nother/modules/dir'))

        self.load_modules.assert_called_once_with(
            modules_dirs=('/tmp/modules/dir', '/tmp/a/nother/modules/dir')
        )

    def test_load_unresolved_modules_resolves_prototypes_if_module_prototype_in_config(self):
        load_unresolved_modules()

        self.resolve_prototypes.assert_called_once_with(
            {'a': 'prototype'},
            self.load_modules.return_value
        )

    def test_load_unresolved_modules_un_resolves_prototypes_again(self):
        ret = load_unresolved_modules()

        self.un_resolve_prototypes.assert_called_once_with(
            {'a': 'prototype'},
            self.resolve_prototypes.return_value
        )
        self.assertEqual(ret, self.un_resolve_prototypes.return_value)

    def test_load_unresolved_modules_does_not_resolve_and_unresolve_prototypes_if_no_prototype_in_config(self):
        self.load_modules.return_value = {'there': 'are_no_prototypes_in_this_config'}

        ret = load_unresolved_modules()

        self.assertFalse(self.resolve_prototypes.called)
        self.assertFalse(self.un_resolve_prototypes.called)
        self.assertEqual(ret, self.load_modules.return_value)
