from raptiformica.shell.ssh import detached_command_context
from tests.testcase import TestCase


class TestDetachedCommandContext(TestCase):
    def setUp(self):
        self.run_detached_command = self.set_up_patch(
            'raptiformica.shell.ssh.run_detached_command'
        )
        self.run_detached_command.return_value = 'screen1234'
        self.run_command_print_ready = self.set_up_patch(
            'raptiformica.shell.ssh.run_command_print_ready'
        )

    def test_detached_command_context_runs_detached_command_before_entering_context(self):
        with detached_command_context('sleep 5'):
            self.run_detached_command.assert_called_once_with(
                'sleep 5'
            )

    def test_detached_command_context_does_not_kill_detached_command_after_leaving_context(self):
        with detached_command_context('sleep 5'):
            pass

        self.assertFalse(self.run_command_print_ready.called)

    def test_detached_command_context_kills_detached_command_after_leaving_context_if_specified(self):
        with detached_command_context('sleep 5', persist=False):
            self.assertFalse(self.run_command_print_ready.called)

        self.run_command_print_ready.assert_called_once_with(
            'pkill -9 -f screen1234', shell=True
        )

