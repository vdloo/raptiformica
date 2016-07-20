from raptiformica.shell.config import run_configured_bootstrap_command_success
from tests.testcase import TestCase


class TestRunConfiguredBootstrapCommandSuccess(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.config.log')
        self.process_output = (0, 'standard out output', None)
        self.print = self.set_up_patch('raptiformica.shell.config.print')

    def test_run_configured_bootstrap_command_success_logs_success_message(self):
        run_configured_bootstrap_command_success(self.process_output)

        self.assertTrue(self.log.info.called)

    def test_run_configured_boostrap_command_success_prints_standard_output(self):
        run_configured_bootstrap_command_success(self.process_output)

        self.print.assert_called_once_with('standard out output')
