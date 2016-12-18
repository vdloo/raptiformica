from raptiformica.shell.config import run_resource_command
from tests.testcase import TestCase


class TestRunResourceCommand(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.config.log')
        self.resource_command = './papply.sh manifests/headless.pp'
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_run_resource_command_logs_running_configured_resource_command_message(self):
        run_resource_command(self.resource_command, 'puppetfiles', '1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_run_resource_command_runs_command_remotely_print_ready(self):
        run_resource_command(self.resource_command, 'puppetfiles', '1.2.3.4', port=2222)

        expected_remote_command = "/usr/bin/env ssh -A " \
                                  "-o ConnectTimeout=5 " \
                                  "-o StrictHostKeyChecking=no " \
                                  "-o UserKnownHostsFile=/dev/null " \
                                  "-o PasswordAuthentication=no " \
                                  "root@1.2.3.4 -p 2222 " \
                                  "'cd /usr/etc/puppetfiles; " \
                                  "./papply.sh manifests/headless.pp'"
        self.execute_process.assert_called_once_with(
            expected_remote_command,
            buffered=False,
            shell=True
        )

    def test_run_resource_command_returns_command_output(self):
        ret = run_resource_command(self.resource_command, 'puppetfiles', '1.2.3.4', port=2222)

        self.assertEqual(ret, 0)

