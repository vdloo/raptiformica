from mock import Mock

from raptiformica.shell.ssh import get_ssh_connection
from tests.testcase import TestCase


class TestGetSSHConnection(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.ssh.log')
        self.host_and_port_pairs = [
            ('1.1.1.1', '22'),
            ('1.1.1.2', '2222'),
            ('1.1.1.3', '2202'),
        ]
        self.try_machine_command = self.set_up_patch(
            'raptiformica.shell.ssh.try_machine_command'
        )
        self.try_machine_command.return_value = ('1', '1.1.1.2', '2222')

    def test_get_ssh_connection_logs_getting_ssh_connection_message(self):
        get_ssh_connection(self.host_and_port_pairs)

        self.assertTrue(self.log.debug.called)

    def test_get_ssh_connection_tries_machine_echoing_in_remote_shell(self):
        get_ssh_connection(self.host_and_port_pairs)

        expected_command = ['/bin/echo', '1']
        self.try_machine_command.assert_called_once_with(
            self.host_and_port_pairs,
            expected_command,
            attempt_message="Trying to get a shell on {}:{}",
            all_failed_message="Failed to get an SSH connection. No available."
        )

    def test_get_ssh_connection_returns_first_connecting_host_and_port(self):
        host, port = get_ssh_connection(self.host_and_port_pairs)

        self.assertEqual(host, '1.1.1.2')
        self.assertEqual(port, '2222')
