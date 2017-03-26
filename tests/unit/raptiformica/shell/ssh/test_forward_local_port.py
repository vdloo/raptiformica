from uuid import uuid4

from raptiformica.shell.ssh import forward_local_port
from tests.testcase import TestCase


class TestForwardLocalPort(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.shell.ssh.log'
        )
        self.run_detached_command = self.set_up_patch(
            'raptiformica.shell.ssh.run_detached_command',
            return_value=str(uuid4())
        )
        self.sleep = self.set_up_patch(
            'raptiformica.shell.ssh.sleep'
        )
        self.run_command_print_ready = self.set_up_patch(
            'raptiformica.shell.ssh.run_command_print_ready'
        )

    def test_forward_local_port_logs_debug_before_context(self):
        with forward_local_port('127.0.0.1', 22):
            self.assertTrue(self.log.debug.called)

    def test_forward_local_port_runs_forward_command_before_context(self):
        self.assertFalse(self.run_detached_command.called)

        with forward_local_port('127.0.0.1', 22):
            self.run_detached_command.assert_called_once_with(
                'ssh root@127.0.0.1 -p 22 '
                '-oStrictHostKeyChecking=no '
                '-oUserKnownHostsFile=/dev/null '
                '-oPasswordAuthentication=no '
                '-R 22:localhost:22 sleep 600'
            )

    def test_forward_local_port_gives_the_tunnel_some_time_to_establish(self):
        self.assertFalse(self.sleep.called)

        with forward_local_port('127.0.0.1', 22):
            self.sleep.assert_called_once_with(1)

    def test_forward_local_port_kills_forward_after_context(self):
        with forward_local_port('127.0.0.1', 22):
            self.assertFalse(self.run_command_print_ready.called)

        self.run_command_print_ready.assert_called_once_with(
            'pkill -9 -f {}'.format(
                self.run_detached_command.return_value
            ),
            shell=True
        )

