from raptiformica.shell.cjdns import cjdns_setup
from raptiformica.shell.execute import COMMAND_TIMEOUT
from tests.testcase import TestCase


class TestCjdnsSetup(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.cjdns.log')
        self.execute_process = self.set_up_patch(
                'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_cjdns_setup_logs_building_and_configuring_and_installing_cjdns_message(self):
        cjdns_setup('1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_cjdns_setup_runs_cjdns_setup_script(self):
        cjdns_setup('1.2.3.4', port=2222)

        expected_command = "/usr/bin/env ssh -A " \
                           "-o ConnectTimeout=5 " \
                           "-o StrictHostKeyChecking=no " \
                           '-o ServerAliveInterval=10 ' \
                           '-o ServerAliveCountMax=3 ' \
                           "-o UserKnownHostsFile=/dev/null " \
                           "-o PasswordAuthentication=no " \
                           "root@1.2.3.4 -p 2222 " \
                           "'cd /usr/etc/cjdns; " \
                           "/usr/etc/raptiformica/resources/setup_cjdns.sh'"
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=False,
            shell=True,
            timeout=COMMAND_TIMEOUT
        )

    def test_cjdns_setup_raises_error_when_cjdns_setup_script_fails(self):
        self.process_output = (1, 'standard out output', 'standard error output')
        self.execute_process.return_value = self.process_output

        with self.assertRaises(RuntimeError):
            cjdns_setup('1.2.3.4', port=2222)

    def test_cjdns_setup_returns_exit_code_from_setup_command(self):
        ret = cjdns_setup('1.2.3.4', port=2222)

        self.assertEqual(ret, 0)

