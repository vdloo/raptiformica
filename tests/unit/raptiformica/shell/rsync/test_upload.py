from raptiformica.settings import PROJECT_DIR, INSTALL_DIR
from raptiformica.shell.rsync import upload
from tests.testcase import TestCase


class TestUpload(TestCase):
    def setUp(self):
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_upload_runs_upload_command(self):
        upload(PROJECT_DIR, INSTALL_DIR, '1.2.3.4', port=22)

        expected_upload_command = [
            '/usr/bin/env', 'rsync', '-L', '-avz', PROJECT_DIR,
            'root@1.2.3.4:{}'.format(INSTALL_DIR), '--exclude=.venv',
            '--exclude', '*.pyc', '-e',
            'ssh -p 22 '
            '-oStrictHostKeyChecking=no '
            '-oUserKnownHostsFile=/dev/null'
        ]
        self.execute_process.assert_called_once_with(
            expected_upload_command,
            buffered=False,
            shell=False
        )

    def test_upload_raises_error_when_uploading_self_failed(self):
        self.process_output = (1, '', 'standard error output')
        self.execute_process.return_value = self.process_output

        with self.assertRaises(RuntimeError):
            upload(PROJECT_DIR, INSTALL_DIR, '1.2.3.4', port=22)

    def test_upload_returns_command_exit_code(self):
        ret = upload(PROJECT_DIR, INSTALL_DIR, '1.2.3.4', port=22)

        self.assertEqual(ret, 0)
