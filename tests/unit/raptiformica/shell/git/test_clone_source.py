from raptiformica.shell.git import clone_source, clone_source_failure
from tests.testcase import TestCase


class TestCloneSource(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.git.log')
        self.run_command_remotely_print_ready = self.set_up_patch(
                'raptiformica.shell.git.run_command_remotely_print_ready'
        )

    def test_clone_source_logs_cloning_source_message(self):
        clone_source(
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles',
            '1.2.3.4',
            port=22
        )

        self.assertTrue(self.log.info.called)

    def test_clone_source_runs_clone_source_command_on_remote_host(self):
        clone_source(
                'https://github.com/vdloo/puppetfiles',
                '/usr/etc/puppetfiles',
                '1.2.3.4',
                port=22
        )

        expected_command = [
            '/usr/bin/env', 'git', 'clone',
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles'
        ]
        self.run_command_remotely_print_ready.assert_called_once_with(
            expected_command,
            '1.2.3.4',
            port=22,
            failure_callback=clone_source_failure
        )

    def test_clone_source_returns_clone_source_command_exit_code(self):
        ret = clone_source(
                'https://github.com/vdloo/puppetfiles',
                '/usr/etc/puppetfiles',
                '1.2.3.4',
                port=22
        )

        self.assertEqual(ret, self.run_command_remotely_print_ready.return_value)
