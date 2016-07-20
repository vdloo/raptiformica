from raptiformica.shell.git import reset_hard_origin_master, reset_hard_origin_master_failure
from tests.testcase import TestCase


class TestResetHardOriginMaster(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.git.log')
        self.run_command_remotely_print_ready = self.set_up_patch(
            'raptiformica.shell.git.run_command_remotely_print_ready'
        )

    def test_that_reset_hard_origin_master_logs_resetting_origin_master_message(self):
        reset_hard_origin_master('/usr/etc/puppetfiles', '1.2.3.4', port=22)

        self.assertTrue(self.log.info.called)

    def test_that_reset_hard_origin_master_runs_reset_hard_origin_master_command(self):
        reset_hard_origin_master('/usr/etc/puppetfiles', '1.2.3.4', port=22)

        expected_command = [
            'cd', '/usr/etc/puppetfiles', ';',
            '/usr/bin/env', 'git', 'reset',
            '--hard', 'origin/master'
        ]
        self.run_command_remotely_print_ready.assert_called_once_with(
            expected_command,
            '1.2.3.4',
            port=22,
            failure_callback=reset_hard_origin_master_failure
        )

    def test_that_reset_hard_origin_master_returns_exit_code(self):
        ret = reset_hard_origin_master('/usr/etc/puppetfiles', '1.2.3.4', port=22)

        self.assertEqual(ret, self.run_command_remotely_print_ready.return_value)
