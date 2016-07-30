from raptiformica.shell.config import run_configured_bootstrap_command
from tests.testcase import TestCase


class TestRunConfiguredBootstrapCommand(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.config.log')
        self.bootstrap_command = './papply.sh manifests/headless.pp'
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_run_configured_bootstrap_command_logs_running_configured_bootstrap_command_message(self):
        run_configured_bootstrap_command(self.bootstrap_command, 'puppetfiles', '1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_run_configured_bootstrap_command_runs_command_remotely_print_ready(self):
        run_configured_bootstrap_command(self.bootstrap_command, 'puppetfiles', '1.2.3.4', port=2222)

        expected_remote_command = [
            '/usr/bin/env', 'ssh',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            'root@1.2.3.4', '-p', '2222',
            'cd', '/usr/etc/puppetfiles',
            ';', './papply.sh manifests/headless.pp'
        ]
        self.execute_process.assert_called_once_with(
            expected_remote_command,
            buffered=False,
            shell=False
        )

    def test_run_configured_bootstrap_command_returns_command_output(self):
        ret = run_configured_bootstrap_command(self.bootstrap_command, 'puppetfiles', '1.2.3.4', port=2222)

        self.assertEqual(ret, 0)

