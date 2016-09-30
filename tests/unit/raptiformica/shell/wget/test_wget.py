from raptiformica.shell.wget import wget
from tests.testcase import TestCase


class TestWget(TestCase):
    def setUp(self):
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', 'standard error output')
        self.execute_process.return_value = self.process_output

    def test_wget_runs_wget_command(self):
        wget(
            'https://www.example.com/some_url.zip',
            '1.2.3.4', port=22,
            failure_message='Failed retrieving the file'
        )

        expected_command = [
            '/usr/bin/env', 'ssh',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'PasswordAuthentication=no',
            'root@1.2.3.4', '-p', '22',
            'wget', '-nc', 'https://www.example.com/some_url.zip'
        ]
        self.execute_process.assert_called_once_with(
                expected_command,
                buffered=False,
                shell=False
        )

    def test_wget_raises_error_when_retrieving_the_file_failed(self):
        self.process_output = (1, 'standard out output', 'standard error output')
        self.execute_process.return_value = self.process_output

        with self.assertRaises(RuntimeError):
            wget(
                'https://www.example.com/some_url.zip',
                '1.2.3.4', port=22,
                failure_message='Failed retrieving the file'
            )
