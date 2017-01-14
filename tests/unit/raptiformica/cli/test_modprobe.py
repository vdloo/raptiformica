from raptiformica.cli import modprobe
from tests.testcase import TestCase


class TestModprobe(TestCase):
    def setUp(self):
        self.parse_modprobe_arguments = self.set_up_patch(
            'raptiformica.cli.parse_modprobe_arguments'
        )
        self.unload_module = self.set_up_patch(
            'raptiformica.cli.unload_module'
        )
        self.load_module = self.set_up_patch(
            'raptiformica.cli.load_module'
        )

    def test_modprobe_parses_modprobe_arguments(self):
        modprobe()

        self.parse_modprobe_arguments.assert_called_once_with()

    def test_modprobe_unloads_module_if_remove_is_specified(self):
        self.parse_modprobe_arguments.return_value.remove = True

        modprobe()

        self.unload_module.assert_called_once_with(
            self.parse_modprobe_arguments.return_value.name
        )
        self.assertFalse(self.load_module.called)

    def test_modprobe_loads_module(self):
        self.parse_modprobe_arguments.return_value.remove = False

        modprobe()

        self.load_module.assert_called_once_with(
            self.parse_modprobe_arguments.return_value.name
        )
        self.assertFalse(self.unload_module.called)
