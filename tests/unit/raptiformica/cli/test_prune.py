from raptiformica.cli import prune
from tests.testcase import TestCase


class TestPrune(TestCase):
    def setUp(self):
        self.parse_prune_arguments = self.set_up_patch(
            'raptiformica.cli.parse_prune_arguments'
        )
        # patching the original function instead of the function in the scope
        # of cli.py because this is a conditional import and so that function
        # won't be available to patch until the function that imports it is
        # evaluated.
        self.prune_local_machines = self.set_up_patch(
            'raptiformica.actions.prune.prune_local_machines'
        )

    def test_prune_parses_prune_arguments(self):
        prune()

        self.parse_prune_arguments.assert_called_once_with()

    def test_prune_prunes_local_machines(self):
        prune()

        self.prune_local_machines.assert_called_once_with()
