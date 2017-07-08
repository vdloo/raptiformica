from raptiformica.actions.mesh import ensure_raptiformica_agent
from tests.testcase import TestCase


class TestEnsureRaptiformicaAgent(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.execute_process = self.set_up_patch(
                'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_ensure_raptiformica_agent_logs_starting_agent_message(self):
        ensure_raptiformica_agent()

        self.log.info.assert_called_once_with("Ensuring raptiformica agent is running")

    def test_ensure_raptiformica_agent_starts_detached_raptiformica_agent(self):
        ensure_raptiformica_agent()

        expected_command = "/usr/bin/env screen -d -m " \
                           "sh -c 'PYTHONPATH=/usr/etc/raptiformica " \
                           "python3 /usr/etc/raptiformica/bin/" \
                           "raptiformica_agent.py'"
        self.execute_process.assert_called_once_with(
            expected_command,
            shell=True,
            buffered=False,
            timeout=1800
        )

    def test_ensure_raptiformica_agent_raises_error_when_starting_agent_failed(self):
        process_output = (1, 'standard out output', 'standard error output')
        self.execute_process.return_value = process_output
        with self.assertRaises(RuntimeError):
            ensure_raptiformica_agent()
