from raptiformica.shell.consul import unzip_consul_binary
from tests.testcase import TestCase


class TestUnzipConsulBinary(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.consul.log')
        self.execute_process = self.set_up_patch(
                'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_unzip_consul_binary_logs_ensuring_latest_consul_release_message(self):
        unzip_consul_binary('1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_unzip_consul_binary_downloads_latest_consul_release_with_no_clobber(self):
        unzip_consul_binary('1.2.3.4', port=2222)

        expected_command = [
            '/usr/bin/env', 'ssh',
            '-o', 'ConnectTimeout=5',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'PasswordAuthentication=no',
            'root@1.2.3.4',
            '-p', '2222', 'unzip', '-o',
            'consul_0.7.0_linux_amd64.zip',
            '-d', '/usr/bin'
        ]
        self.execute_process.assert_called_once_with(
                expected_command,
                buffered=False,
                shell=False
        )

    def test_unzip_consul_binary_raises_error_when_ensuring_latest_release_fails(self):
        self.execute_process.return_value = (1, 'standard out output', 'standard error output')

        with self.assertRaises(RuntimeError):
            unzip_consul_binary('1.2.3.4', port=2222)
