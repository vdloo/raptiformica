from raptiformica.actions.ssh_connect import ssh_connect
from tests.testcase import TestCase


class TestSSHConnect(TestCase):
    def setUp(self):
        self.host_and_port_pairs_from_mutable_config = self.set_up_patch(
            'raptiformica.actions.ssh_connect.host_and_port_pairs_from_config'
        )
        self.get_ssh_connection = self.set_up_patch(
            'raptiformica.actions.ssh_connect.get_ssh_connection'
        )
        self.system = self.set_up_patch(
            'raptiformica.actions.ssh_connect.system'
        )
        self.print = self.set_up_patch(
            'raptiformica.actions.ssh_connect.print'
        )
        self.get_ssh_connection.return_value = ('127.0.0.1', '22')

    def test_ssh_connect_gets_host_and_port_pairs_from_mutable_config(self):
        ssh_connect()

        self.host_and_port_pairs_from_mutable_config.assert_called_once_with()

    def test_ssh_connect_gets_ssh_connection_from_host_and_port_pairs(self):
        ssh_connect()

        self.get_ssh_connection.assert_called_once_with(
            self.host_and_port_pairs_from_mutable_config.return_value
        )

    def test_ssh_connect_gets_system_shell_with_ssh_command(self):
        ssh_connect()

        self.system.assert_called_once_with(
            'ssh root@127.0.0.1 -p 22 -oStrictHostKeyChecking=no '
            '-oUserKnownHostsFile=/dev/null -oPasswordAuthentication=no'
        )
        self.assertFalse(self.print.called)

    def test_ssh_connect_only_prints_ssh_command_if_info_only_is_specified(self):
        ssh_connect(info_only=True)

        self.assertFalse(self.system.called)
        self.print.assert_called_once_with(
            'ssh root@127.0.0.1 -p 22 -oStrictHostKeyChecking=no '
            '-oUserKnownHostsFile=/dev/null -oPasswordAuthentication=no'
        )
