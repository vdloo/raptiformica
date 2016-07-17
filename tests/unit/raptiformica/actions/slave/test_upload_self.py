from raptiformica.actions.slave import upload_self
from raptiformica.settings import PROJECT_DIR, INSTALL_DIR
from tests.testcase import TestCase


class TestUploadSelf(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.slave.log')
        self.run_command = self.set_up_patch('raptiformica.actions.slave.run_command')
        self.standard_out = 'standard out output'
        self.standard_err = 'standard error output'
        self.run_command.return_value = (0, self.standard_out, self.standard_err)

    def test_upload_self_runs_upload_command(self):
        upload_self('1.2.3.4')

        expected_command = [
            '/usr/bin/env', 'rsync', '-avz',
            '{}'.format(PROJECT_DIR), 'root@{}:{}'.format('1.2.3.4', INSTALL_DIR),
            '--exclude=var/machines', "--exclude=*.pyc'",
            '-e', 'ssh -p {}'.format(22)
        ]
        self.run_command.assert_called_once_with(expected_command)

    def test_upload_self_runs_upload_command_with_specified_port_if_provided(self):
        custom_port = 2222

        upload_self('1.2.3.4', port=custom_port)

        expected_command = [
            '/usr/bin/env', 'rsync', '-avz',
            '{}'.format(PROJECT_DIR), 'root@{}:{}'.format('1.2.3.4', INSTALL_DIR),
            '--exclude=var/machines', "--exclude=*.pyc'",
            '-e', 'ssh -p {}'.format(2222)
        ]
        self.run_command.assert_called_once_with(expected_command)

    def test_upload_self_logs_to_info_when_uploading_self_succeeded(self):
        upload_self('1.2.3.4')

        self.log.info.assert_called_once_with('Uploaded raptiformica to the remote host')
        self.log.debug.assert_called_once_with(self.standard_out)

    def test_upload_self_raises_error_when_uploading_self_fails(self):
        self.run_command.return_value = (1, self.standard_out, self.standard_err)

        with self.assertRaises(RuntimeError):
            upload_self('1.2.3.4')

        self.assertFalse(self.log.info.called)
