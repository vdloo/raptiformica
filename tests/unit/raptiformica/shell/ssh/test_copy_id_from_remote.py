from raptiformica.shell.ssh import copy_id_from_remote
from tests.testcase import TestCase


class TestCopyIdFromRemote(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.shell.ssh.log'
        )
        self.run_critical_command_print_ready = self.set_up_patch(
            'raptiformica.shell.ssh.run_critical_command_print_ready'
        )

    def test_copy_id_from_remote_copies_the_public_key_from_the_remote_server(self):
        copy_id_from_remote('1.2.3.4')

        expected_command = 'ssh root@1.2.3.4 -p 22 ' \
                           '-oStrictHostKeyChecking=no ' \
                           '-oUserKnownHostsFile=/dev/null ' \
                           '-oPasswordAuthentication=no ' \
                           'cat .ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys'
        expected_failure_message = 'Failed to copy the ID from 1.2.3.4:22 ' \
                                   'to the local authorized keys file'
        self.run_critical_command_print_ready.assert_called_once_with(
            expected_command, buffered=False, shell=True,
            failure_message=expected_failure_message
        )

    def test_copy_id_from_remote_uses_specified_port(self):
        copy_id_from_remote('1.2.3.4', ssh_port=1234)

        expected_command = 'ssh root@1.2.3.4 -p 1234 ' \
                           '-oStrictHostKeyChecking=no ' \
                           '-oUserKnownHostsFile=/dev/null ' \
                           '-oPasswordAuthentication=no ' \
                           'cat .ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys'
        expected_failure_message = 'Failed to copy the ID from 1.2.3.4:1234 ' \
                                   'to the local authorized keys file'
        self.run_critical_command_print_ready.assert_called_once_with(
            expected_command, buffered=False, shell=True,
            failure_message=expected_failure_message
        )

