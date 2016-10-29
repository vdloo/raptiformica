from raptiformica.cli import prune
from tests.testcase import TestCase


class TestPrune(TestCase):
    def setUp(self):
        self.parse_prune_arguments = self.set_up_patch('raptiformica.cli.parse_prune_arguments')
        self.prune_local_machines = self.set_up_patch('raptiformica.cli.prune_local_machines')

    def test_prune_parses_prune_arguments(self):
        prune()

        self.parse_prune_arguments.assert_called_once_with()

    def test_prune_prunes_local_machines(self):
        prune()

        self.prune_local_machines.assert_called_once_with()
