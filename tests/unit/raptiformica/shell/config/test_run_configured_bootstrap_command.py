from raptiformica.shell.config import run_configured_bootstrap_command, run_configured_bootstrap_command_failure, \
    run_configured_bootstrap_command_success
from tests.testcase import TestCase


class TestRunConfiguredBootstrapCommand(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.config.log')
        self.bootstrap_command = './papply.sh manifests/headless.pp'
        self.run_command_remotely_print_ready = self.set_up_patch('raptiformica.shell.config.run_command_remotely_print_ready')

    def test_run_configured_bootstrap_command_logs_running_configured_bootstrap_command_message(self):
        run_configured_bootstrap_command(self.bootstrap_command, 'puppetfiles', '1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_run_configured_bootstrap_command_runs_command_remotely_print_ready(self):
        run_configured_bootstrap_command(self.bootstrap_command, 'puppetfiles', '1.2.3.4', port=2222)

        expected_remote_command = ['cd', '/usr/etc/puppetfiles', ';', self.bootstrap_command]
        self.run_command_remotely_print_ready.assert_called_once_with(
            expected_remote_command, '1.2.3.4', port=2222,
            failure_callback=run_configured_bootstrap_command_failure,
            success_callback=run_configured_bootstrap_command_success
        )

    def test_run_configured_bootstrap_command_returns_command_output(self):
        ret = run_configured_bootstrap_command(self.bootstrap_command, 'puppetfiles', '1.2.3.4', port=2222)

        self.assertEqual(ret, self.run_command_remotely_print_ready.return_value)

