from mock import ANY
from uuid import uuid4

from raptiformica.shell.ssh import run_detached_command
from tests.testcase import TestCase


class TestRunDetachedCommand(TestCase):
    def setUp(self):
        self.uuid4 = self.set_up_patch(
            'raptiformica.shell.ssh.uuid4',
            return_value=uuid4()
        )
        self.screen_name = str(self.uuid4.return_value).replace('-', '')
        self.run_critical_command_print_ready = self.set_up_patch(
            'raptiformica.shell.ssh.run_critical_command_print_ready'
        )

    def test_run_detached_command_runs_detached_command(self):
        run_detached_command("sleep 10")

        expected_command = "/usr/bin/env screen -S " \
                           "{} -d -m bash -c 'sleep 10'" \
                           "".format(self.screen_name)
        self.run_critical_command_print_ready.assert_called_once_with(
            expected_command, buffered=False, shell=True,
            failure_message='Failed running detached command'
        )

    def test_run_detached_command_uses_specified_failure_message(self):
        run_detached_command(
            "sleep 10",
            failure_message='Custom failure message'
        )

        self.run_critical_command_print_ready.assert_called_once_with(
            ANY, buffered=False, shell=True,
            failure_message='Custom failure message'
        )

    def test_run_detached_command_returns_screen_name(self):
        ret = run_detached_command("sleep 10")

        self.assertEqual(ret, self.screen_name)
