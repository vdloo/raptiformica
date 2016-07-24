from raptiformica.shell.git import clone_source_remotely
from tests.testcase import TestCase


class TestCloneSourceRemotely(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.git.log')
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_clone_source_remotely_logs_cloning_source_message(self):
        clone_source_remotely(
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles',
            '127.0.0.1', port=2222
        )

        self.assertTrue(self.log.info.called)

    def test_clone_source_remotely_runs_clone_source_remotely(self):
        clone_source_remotely(
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles',
            '127.0.0.1', port=2222
        )

        expected_command = [
            '/usr/bin/env', 'ssh', 'root@127.0.0.1', '-p', '2222',
            '-o', 'StrictHostKeyChecking=no',
            '/usr/bin/env', 'git', 'clone',
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles'
        ]
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=False
        )

    def test_clone_source_remotely_returns_clone_source_remotely_command_exit_code(self):
        ret = clone_source_remotely(
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles',
            '127.0.0.1', port=2222
        )

        self.assertEqual(ret, 0)
