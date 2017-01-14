from raptiformica.cli import ssh
from tests.testcase import TestCase


class TestSSH(TestCase):
    def setUp(self):
        self.parse_ssh_arguments = self.set_up_patch(
            'raptiformica.cli.parse_ssh_arguments'
        )
        # patching the original function instead of the function in the scope
        # of cli.py because this is a conditional import and so that function
        # won't be available to patch until the function that imports it is
        # evaluated.
        self.ssh_connect = self.set_up_patch(
            'raptiformica.actions.ssh_connect.ssh_connect'
        )

    def test_ssh_parses_ssh_arguments(self):
        ssh()

        self.parse_ssh_arguments.assert_called_once_with()

    def test_ssh_shows_ssh(self):
        ssh()

        self.ssh_connect.assert_called_once_with(
            info_only=self.parse_ssh_arguments.return_value.info_only
        )
