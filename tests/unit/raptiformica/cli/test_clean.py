from raptiformica.cli import clean
from tests.testcase import TestCase


class TestClean(TestCase):
    def setUp(self):
        self.parse_clean_arguments = self.set_up_patch(
            'raptiformica.cli.parse_clean_arguments'
        )
        self.clean_local_state = self.set_up_patch(
            'raptiformica.cli.clean_local_state'
        )

    def test_clean_parses_clean_arguments(self):
        clean()

        self.parse_clean_arguments.assert_called_once_with()

    def test_clean_cleans_local_machines(self):
        clean()

        self.clean_local_state.assert_called_once_with()
