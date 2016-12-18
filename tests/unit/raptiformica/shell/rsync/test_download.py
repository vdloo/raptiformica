from raptiformica.settings import PROJECT_DIR, INSTALL_DIR
from raptiformica.shell.rsync import download
from tests.testcase import TestCase


class TestDownload(TestCase):
    def setUp(self):
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_download_runs_download_command(self):
        download(PROJECT_DIR, INSTALL_DIR, '1.2.3.4', port=22)

        expected_download_command = [
            '/usr/bin/env', 'rsync', '-q', '--force', '-avz',
            '-ignore-missing-args',  # Don't warn when downloading from self
            'root@1.2.3.4:{}'.format(PROJECT_DIR),
            INSTALL_DIR, '--exclude=.venv',
            '--exclude=*.pyc', '-e', 'ssh -p 22 '
            '-oStrictHostKeyChecking=no '
            '-oUserKnownHostsFile=/dev/null'
        ]
        self.execute_process.assert_called_once_with(
            expected_download_command,
            buffered=False,
            shell=False
        )

    def test_download_raises_error_when_downloading_failed(self):
        self.process_output = (1, '', 'standard error output')
        self.execute_process.return_value = self.process_output

        with self.assertRaises(RuntimeError):
            download(PROJECT_DIR, INSTALL_DIR, '1.2.3.4', port=22)

    def test_download_returns_command_exit_code(self):
        ret = download(PROJECT_DIR, INSTALL_DIR, '1.2.3.4', port=22)

        self.assertEqual(ret, 0)
