from raptiformica.shell.config import run_configured_bootstrap_command_failure
from tests.testcase import TestCase


class TestRunConfiguredBootstrapCommandFailure(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.config.log')
        self.process_output = (1, 'standard out output', 'standard error output')
        self.print = self.set_up_patch('raptiformica.shell.config.print')

    def test_run_configured_bootstrap_command_failure_logs_failure_message(self):
        run_configured_bootstrap_command_failure(self.process_output)

        self.assertTrue(self.log.warning.called)

    def test_run_configured_bootstrap_command_failure_prints_standard_output(self):
        run_configured_bootstrap_command_failure(self.process_output)

        self.print.assert_called_once_with('standard out output')
