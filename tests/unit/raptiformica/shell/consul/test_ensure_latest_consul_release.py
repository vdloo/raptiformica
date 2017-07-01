from mock import call

from raptiformica.shell.consul import ensure_latest_consul_release
from tests.testcase import TestCase


class TestEnsureLatestConsulRelease(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.consul.log')
        self.execute_process = self.set_up_patch(
                'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_ensure_latest_consul_release_logs_ensuring_latest_consul_release_message(self):
        ensure_latest_consul_release('1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_ensure_latest_consul_release_downloads_latest_consul_release_with_no_clobber(self):
        ensure_latest_consul_release('1.2.3.4', port=2222)

        expected_binary_command = [
            '/usr/bin/env', 'ssh', '-A',
            '-o', 'ConnectTimeout=5',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'PasswordAuthentication=no',
            'root@1.2.3.4',
            '-p', '2222', 'wget', '-nc',
            'https://releases.hashicorp.com/consul/0.8.5/consul_0.8.5_linux_amd64.zip'
        ]
        expected_web_ui_command = [
            '/usr/bin/env', 'ssh', '-A',
            '-o', 'ConnectTimeout=5',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'PasswordAuthentication=no',
            'root@1.2.3.4',
            '-p', '2222', 'wget', '-nc',
            'https://releases.hashicorp.com/consul/0.8.5/consul_0.8.5_web_ui.zip'
        ]
        expected_calls = [
            call(expected_binary_command, buffered=False, shell=False),
            call(expected_web_ui_command, buffered=False, shell=False)
        ]
        self.assertCountEqual(self.execute_process.mock_calls, expected_calls)

    def test_ensure_latest_consul_release_raises_error_when_ensuring_latest_release_fails(self):
        self.execute_process.return_value = (1, 'standard out output', '')

        with self.assertRaises(RuntimeError):
            ensure_latest_consul_release('1.2.3.4', port=2222)

    def test_ensure_latest_consul_release_raises_error_when_ensuring_web_ui_fails(self):
        self.execute_process.side_effect = [
            self.execute_process.return_value, (1, 'standard out output', '')
        ]

        with self.assertRaises(RuntimeError):
            ensure_latest_consul_release('1.2.3.4', port=2222)
