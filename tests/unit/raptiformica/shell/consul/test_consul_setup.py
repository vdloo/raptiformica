from os.path import join

from raptiformica.settings import RAPTIFORMICA_DIR
from raptiformica.shell.consul import consul_setup
from tests.testcase import TestCase


class TestConsulSetup(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.consul.log')
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_consul_setup_logs_consul_setup_message(self):
        consul_setup('1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_consul_setup_runs_consul_setup_script(self):
        consul_setup('1.2.3.4', port=2222)

        expected_command = [
            '/usr/bin/env', 'ssh',
            '-o', 'ConnectTimeout=5',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'PasswordAuthentication=no',
            'root@1.2.3.4', '-p', '2222',
            join(RAPTIFORMICA_DIR, 'resources/setup_consul.sh')
        ]
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=False,
            shell=False
        )

    def test_consul_setup_raises_error_when_consul_setup_script_fails(self):
        self.process_output = (1, 'standard out output', 'standard error output')
        self.execute_process.return_value = self.process_output

        with self.assertRaises(RuntimeError):
            consul_setup('1.2.3.4', port=2222)

    def test_consul_setup_returns_exit_code_from_setup_command(self):
        ret = consul_setup('1.2.3.4', port=2222)

        self.assertEqual(ret, 0)
