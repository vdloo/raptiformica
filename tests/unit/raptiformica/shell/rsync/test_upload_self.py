from raptiformica.settings import PROJECT_DIR, INSTALL_DIR
from raptiformica.shell.rsync import upload_self, upload_self_success, upload_self_failure
from tests.testcase import TestCase


class TestUploadSelf(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.rsync.log')
        self.run_command_print_ready = self.set_up_patch('raptiformica.shell.rsync.run_command_print_ready')

    def test_upload_self_logs_uploading_self_message(self):
        upload_self('1.2.3.4', port=22)

        self.assertTrue(self.log.info.called)

    def test_upload_self_runs_upload_command(self):
        upload_self('1.2.3.4', port=22)

        expected_upload_command = [
            '/usr/bin/env', 'rsync', '-L', '-avz', PROJECT_DIR,
            'root@1.2.3.4:{}'.format(INSTALL_DIR), '--exclude=var/machines',
            '--exclude', '*.pyc', '-e', 'ssh -p 22'
        ]
        self.run_command_print_ready.assert_called_once_with(
            expected_upload_command,
            success_callback=upload_self_success,
            failure_callback=upload_self_failure
        )

