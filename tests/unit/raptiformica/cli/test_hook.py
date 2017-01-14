from raptiformica.cli import hook
from tests.testcase import TestCase


class TestHook(TestCase):
    def setUp(self):
        self.parse_hook_arguments = self.set_up_patch(
            'raptiformica.cli.parse_hook_arguments'
        )
        # patching the original function instead of the function in the scope
        # of cli.py because this is a conditional import and so that function
        # won't be available to patch until the function that imports it is
        # evaluated.
        self.trigger_handlers = self.set_up_patch(
            'raptiformica.actions.hook.trigger_handlers'
        )

    def test_hook_parses_hook_arguments(self):
        hook()

        self.parse_hook_arguments.assert_called_once_with()

    def test_hook_shows_hook(self):
        hook()

        self.trigger_handlers.assert_called_once_with(
            hook_name=self.parse_hook_arguments.return_value.name
        )
