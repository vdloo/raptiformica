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

        expected_command = [
            '/usr/bin/env', 'ssh', '-o',
            'StrictHostKeyChecking=no', '-o',
            'UserKnownHostsFile=/dev/null', 'root@1.2.3.4',
            '-p', '2222', 'wget', '-nc',
            'https://releases.hashicorp.com/consul/0.6.4/consul_0.6.4_linux_amd64.zip'
        ]
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=False,
            shell=False
        )

    def test_ensure_latest_consul_release_raises_error_when_ensuring_latest_release_fails(self):
        self.execute_process.return_value = (1, 'standard out output', '')

        with self.assertRaises(RuntimeError):
            ensure_latest_consul_release('1.2.3.4', port=2222)
