from raptiformica.shell.git import clone_source
from tests.testcase import TestCase


class TestCloneSourceRemotely(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.git.log')
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_clone_source_logs_cloning_source_message(self):
        clone_source(
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles',
            host='127.0.0.1', port=2222
        )

        self.assertTrue(self.log.info.called)

    def test_clone_source_runs_clone_source(self):
        clone_source(
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles',
            host='127.0.0.1', port=2222
        )

        expected_command = [
            '/usr/bin/env', 'ssh', '-A',
            '-o', 'ConnectTimeout=5',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'PasswordAuthentication=no',
            'root@127.0.0.1', '-p', '2222',
            '/usr/bin/env', 'git', 'clone',
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles'
        ]
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=False,
            shell=False,
            timeout=1800
        )

    def test_clone_source_returns_clone_source_command_exit_code(self):
        ret = clone_source(
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles',
            host='127.0.0.1', port=2222
        )

        self.assertEqual(ret, 0)
