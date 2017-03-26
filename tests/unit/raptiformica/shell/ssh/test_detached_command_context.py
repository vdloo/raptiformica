from uuid import uuid4

from raptiformica.shell.ssh import detached_command_context
from tests.testcase import TestCase


class TestDetachedCommandContext(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.shell.ssh.log'
        )
        self.run_detached_command = self.set_up_patch(
            'raptiformica.shell.ssh.run_detached_command',
            return_value=str(uuid4())
        )
        self.run_command_print_ready = self.set_up_patch(
            'raptiformica.shell.ssh.run_command_print_ready'
        )

    def test_detached_command_context_logs_to_debug(self):
        with detached_command_context('sleep 10'):
            pass

        self.assertTrue(self.log.debug.called)

    def test_detached_command_context_runs_detached_command_before_yielding_context(self):
        self.assertFalse(self.run_detached_command.called)

        with detached_command_context('sleep 10'):
            self.run_detached_command.assert_called_once_with(
                'sleep 10'
            )

    def test_detached_command_context_kills_detached_command_after_leaving_context(self):
        with detached_command_context('sleep 10'):
            self.assertFalse(self.run_command_print_ready.called)

        self.run_command_print_ready.assert_called_once_with(
            'pkill -9 -f {}'.format(
                self.run_detached_command.return_value
            ),
            shell=True
        )
