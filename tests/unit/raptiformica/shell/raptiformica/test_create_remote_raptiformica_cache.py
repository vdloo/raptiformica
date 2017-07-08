from raptiformica.shell.raptiformica import create_remote_raptiformica_cache
from tests.testcase import TestCase


class TestCreateRemoteRaptiformicaCache(TestCase):
    def setUp(self):
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output
        self.log = self.set_up_patch('raptiformica.shell.raptiformica.log')

    def test_create_remote_raptiformica_cache_logs_creating_remote_cache_message(self):
        create_remote_raptiformica_cache('1.2.3.4', port=1234)

        self.assertTrue(self.log.info.called)

    def test_create_remote_raptiformica_cache_runs_ensure_cache_directory_command(self):
        create_remote_raptiformica_cache('1.2.3.4', port=1234)

        expected_upload_command = [
            '/usr/bin/env', 'ssh', '-A',
            '-o', 'ConnectTimeout=5',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'PasswordAuthentication=no',
            'root@1.2.3.4',
            '-p', '1234', 'mkdir', '-p', '$HOME/.raptiformica.d'
        ]
        self.execute_process.assert_called_once_with(
            expected_upload_command,
            buffered=False,
            shell=False,
            timeout=1800
        )

    def test_create_remote_raptiformica_cache_returns_exit_code_0_if_command_succeeded(self):
        ret = create_remote_raptiformica_cache('1.2.3.4', port=1234)

        self.assertEqual(ret, 0)

    def test_create_remote_raptiformica_cache_returns_exit_code_1_if_command_failed(self):
        self.process_output = (1, 'standard out output', 'standard error output')
        self.execute_process.return_value = self.process_output

        ret = create_remote_raptiformica_cache('1.2.3.4', port=1234)

        self.assertEqual(ret, 1)
