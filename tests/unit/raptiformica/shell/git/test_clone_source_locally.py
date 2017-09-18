from raptiformica.shell.execute import COMMAND_TIMEOUT
from raptiformica.shell.git import clone_source
from tests.testcase import TestCase


class TestCloneSourceLocally(TestCase):
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
        )

        self.assertTrue(self.log.info.called)

    def test_clone_source_runs_clone_source(self):
        clone_source(
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles',
        )

        expected_command = [
            '/usr/bin/env', 'git', 'clone',
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles'
        ]
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=False,
            shell=False,
            timeout=COMMAND_TIMEOUT
        )

    def test_clone_source_returns_clone_source_command_exit_code(self):
        ret = clone_source(
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles',
        )

        self.assertEqual(ret, 0)
