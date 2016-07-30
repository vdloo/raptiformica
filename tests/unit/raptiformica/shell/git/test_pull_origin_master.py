from raptiformica.shell.git import pull_origin_master
from tests.testcase import TestCase


class TestPullOriginMaster(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.git.log')
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_that_pull_origin_master_logs_pulling_origin_master_message(self):
        pull_origin_master('/usr/etc/puppetfiles', '1.2.3.4', port=22)

        self.assertTrue(self.log.info.called)

    def test_that_pull_origin_master_pulls_origin_master_on_remote_host(self):
        pull_origin_master('/usr/etc/puppetfiles', '1.2.3.4', port=22)

        expected_command = [
            '/usr/bin/env', 'ssh',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            'root@1.2.3.4',
            '-p', '22',
            'cd', '/usr/etc/puppetfiles',
            ';', '/usr/bin/env', 'git',
            'pull', 'origin', 'master'
        ]
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=True,
            shell=False
        )

    def test_that_pull_origin_master_returns_pull_origin_master_exit_code(self):
        ret = pull_origin_master('/usr/etc/puppetfiles', '1.2.3.4', port=22)

        self.assertEqual(ret, 0)
