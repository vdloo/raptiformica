from raptiformica.shell.raptiformica import run_raptiformica_command
from tests.testcase import TestCase


class TestRunRaptiformicaCommand(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.raptiformica.log')
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_run_raptiformica_command_logs_running_raptiformica_command_message(self):
        run_raptiformica_command(
            "export PYTHONPATH=.; ./bin/raptiformica_mesh.py --verbose",
            '1.2.3.4', port=2222
        )

        self.assertTrue(self.log.info.called)

    def test_run_raptiformica_command_runs_raptiformica_command_on_the_remote_host(self):
        run_raptiformica_command(
            "export PYTHONPATH=.; ./bin/raptiformica_mesh.py --verbose",
            '1.2.3.4', port=2222
        )

        expected_command = [
            '/usr/bin/env', 'ssh',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            'root@1.2.3.4', '-p', '2222',
            'sh', '-c',
            '"cd /usr/etc/raptiformica; '
            'export PYTHONPATH=.; '
            './bin/raptiformica_mesh.py --verbose"'
        ]
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=False,
            shell=False
        )

    def test_run_raptiformica_command_raises_error_if_remote_raptiformica_command_fails(self):
        process_output = (1, 'standard out output', 'standard error output')
        self.execute_process.return_value = process_output

        with self.assertRaises(RuntimeError):
            run_raptiformica_command(
                "export PYTHONPATH=.; ./bin/raptiformica_mesh.py --verbose",
                '1.2.3.4', port=2222
            )

    def test_run_raptiformica_command_returns_remote_command_exit_code(self):
        ret = run_raptiformica_command(
            "export PYTHONPATH=.; ./bin/raptiformica_mesh.py --verbose",
            '1.2.3.4', port=2222
        )

        self.assertEqual(ret, 0)
