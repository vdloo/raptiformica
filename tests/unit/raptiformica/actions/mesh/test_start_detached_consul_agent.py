from raptiformica.actions.mesh import start_detached_consul_agent
from tests.testcase import TestCase


class TestStartDetachedConsulAgent(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.execute_process = self.set_up_patch(
                'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_start_detached_consul_agent_logs_starting_detached_consul_agent_message(self):
        start_detached_consul_agent()

        self.log.info.assert_called_once_with("Starting a detached consul agent")

    def test_start_detached_consul_agent_starts_detached_consul_agent(self):
        start_detached_consul_agent()

        expected_command = "/usr/bin/env screen -d -m /usr/bin/consul agent --config-dir /etc/consul.d/"
        self.execute_process.assert_called_once_with(
            expected_command,
            shell=True,
            buffered=False
        )

    def test_start_detached_consul_agent_raises_error_when_starting_detached_consul_agent_failed(self):
        process_output = (1, 'standard out output', 'standard error output')
        self.execute_process.return_value = process_output
        with self.assertRaises(RuntimeError):
            start_detached_consul_agent()
