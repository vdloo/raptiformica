from raptiformica.shell.unzip import unzip
from tests.testcase import TestCase


class TestUnzip(TestCase):
    def setUp(self):
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', 'standard error output')
        self.execute_process.return_value = self.process_output

    def test_unzip_runs_unzip_command(self):
        unzip(
            '/tmp/a_zip_file.zip', '/tmp/the_unpack_dir',
            '1.2.3.4', port=22,
            failure_message='The unpacking failed'
        )

        expected_command = [
            '/usr/bin/env', 'ssh',
            '-o', 'ConnectTimeout=5',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'PasswordAuthentication=no',
            'root@1.2.3.4',
            '-p', '22',
            'unzip',
            '-o', '/tmp/a_zip_file.zip',
            '-d', '/tmp/the_unpack_dir'
        ]
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=False,
            shell=False
        )

    def test_unzip_raises_error_when_unzipping_failed(self):
        self.process_output = (1, 'standard out output', 'standard error output')
        self.execute_process.return_value = self.process_output

        with self.assertRaises(RuntimeError):
            unzip(
                    '/tmp/a_zip_file.zip', '/tmp/the_unpack_dir',
                    '1.2.3.4', port=22,
                    failure_message='The unpacking failed'
            )
