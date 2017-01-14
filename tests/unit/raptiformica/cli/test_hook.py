from raptiformica.cli import hook
from tests.testcase import TestCase


class TestHook(TestCase):
    def setUp(self):
        self.parse_hook_arguments = self.set_up_patch(
            'raptiformica.cli.parse_hook_arguments'
        )
        self.trigger_handlers = self.set_up_patch(
            'raptiformica.cli.trigger_handlers'
        )

    def test_hook_parses_hook_arguments(self):
        hook()

        self.parse_hook_arguments.assert_called_once_with()

    def test_hook_shows_hook(self):
        hook()

        self.trigger_handlers.assert_called_once_with(
            hook_name=self.parse_hook_arguments.return_value.name
        )
