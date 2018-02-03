from raptiformica.shell.consul import ensure_latest_consul_release
from tests.testcase import TestCase


class TestEnsureLatestConsulRelease(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.consul.log')
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.remove = self.set_up_patch(
            'raptiformica.shell.consul.remove'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_ensure_latest_consul_release_logs_ensuring_latest_consul_release_message(self):
        ensure_latest_consul_release('1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_ensure_latest_consul_release_removes_previously_existing_zip(self):
        ensure_latest_consul_release('1.2.3.4', port=2222)

        self.remove.assert_called_once_with(
            'consul_1.0.2_linux_amd64.zip'
        )

    def test_ensure_latest_consul_release_ignores_no_previously_existing_zip(self):
        self.remove.side_effect = FileNotFoundError

        # Does not raise FileNotFoundError
        ensure_latest_consul_release('1.2.3.4', port=2222)

    def test_ensure_latest_consul_release_downloads_latest_consul_release_with_no_clobber(self):
        ensure_latest_consul_release('1.2.3.4', port=2222)

        expected_binary_command = [
            '/usr/bin/env', 'ssh', '-A',
            '-o', 'ConnectTimeout=5',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'ServerAliveInterval=10',
            '-o', 'ServerAliveCountMax=3',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'PasswordAuthentication=no',
            'root@1.2.3.4',
            '-p', '2222', 'wget', '-4', '-nc',
            'https://releases.hashicorp.com/consul/1.0.2/consul_1.0.2_linux_amd64.zip'
        ]
        self.execute_process.assert_called_once_with(
            expected_binary_command, buffered=False, shell=False, timeout=15
        )

    def test_ensure_latest_consul_release_raises_error_when_ensuring_latest_release_fails(self):
        self.execute_process.return_value = (1, 'standard out output', '')

        with self.assertRaises(RuntimeError):
            ensure_latest_consul_release('1.2.3.4', port=2222)

