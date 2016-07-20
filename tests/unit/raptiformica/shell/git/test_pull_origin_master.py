from raptiformica.shell.git import pull_origin_master, pull_origin_master_failure
from tests.testcase import TestCase


class TestPullOriginMaster(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.git.log')
        self.run_command_remotely_print_ready = self.set_up_patch(
                'raptiformica.shell.git.run_command_remotely_print_ready'
        )

    def test_that_pull_origin_master_logs_pulling_origin_master_message(self):
        pull_origin_master('/usr/etc/puppetfiles', '1.2.3.4', port=22)

        self.assertTrue(self.log.info.called)

    def test_that_pull_origin_master_pulls_origin_master_on_remote_host(self):
        pull_origin_master('/usr/etc/puppetfiles', '1.2.3.4', port=22)

        expected_command = [
            'cd', '/usr/etc/puppetfiles', ';',
            '/usr/bin/env', 'git', 'pull',
            'origin', 'master'
        ]
        self.run_command_remotely_print_ready.assert_called_once_with(
            expected_command,
            '1.2.3.4',
            port=22,
            failure_callback=pull_origin_master_failure
        )

    def test_that_pull_origin_master_returns_pull_origin_master_exit_code(self):
        ret = pull_origin_master('/usr/etc/puppetfiles', '1.2.3.4', port=22)

        self.assertEqual(ret, self.run_command_remotely_print_ready.return_value)
