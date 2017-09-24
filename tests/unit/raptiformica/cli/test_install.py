from raptiformica.cli import install
from tests.testcase import TestCase


class TestInstall(TestCase):
    def setUp(self):
        self.parse_install_arguments = self.set_up_patch(
            'raptiformica.cli.parse_install_arguments'
        )
        self.unload_module = self.set_up_patch(
            'raptiformica.cli.unload_module'
        )
        self.load_module = self.set_up_patch(
            'raptiformica.cli.load_module'
        )

    def test_install_parses_install_arguments(self):
        install()

        self.parse_install_arguments.assert_called_once_with()

    def test_install_unloads_module_if_remove_is_specified(self):
        self.parse_install_arguments.return_value.remove = True

        install()

        self.unload_module.assert_called_once_with(
            self.parse_install_arguments.return_value.name
        )
        self.assertFalse(self.load_module.called)

    def test_install_loads_module(self):
        self.parse_install_arguments.return_value.remove = False

        install()

        self.load_module.assert_called_once_with(
            self.parse_install_arguments.return_value.name
        )
        self.assertFalse(self.unload_module.called)
