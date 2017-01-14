from raptiformica.cli import update
from tests.testcase import TestCase


class TestUpdate(TestCase):
    def setUp(self):
        self.parse_update_arguments = self.set_up_patch(
            'raptiformica.cli.parse_update_arguments'
        )
        self.update_machine = self.set_up_patch(
            'raptiformica.cli.update_machine'
        )

    def test_update_parses_update_arguments(self):
        update()

        self.parse_update_arguments.assert_called_once_with()

    def test_update_updates_machine_with_specified_server_type(self):
        update()

        self.update_machine.assert_called_once_with(
            server_type=self.parse_update_arguments.return_value.server_type
        )
