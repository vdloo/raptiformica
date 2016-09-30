from raptiformica.cli import ssh
from tests.testcase import TestCase


class TestSSH(TestCase):
    def setUp(self):
        self.parse_ssh_arguments = self.set_up_patch('raptiformica.cli.parse_ssh_arguments')
        self.ssh_connect = self.set_up_patch('raptiformica.cli.ssh_connect')

    def test_ssh_parses_ssh_arguments(self):
        ssh()

        self.parse_ssh_arguments.assert_called_once_with()

    def test_ssh_shows_ssh(self):
        ssh()

        self.ssh_connect.assert_called_once_with(
            info_only=self.parse_ssh_arguments.return_value.info_only
        )
