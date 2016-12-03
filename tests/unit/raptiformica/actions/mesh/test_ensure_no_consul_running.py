from mock import ANY

from raptiformica.actions.mesh import ensure_no_consul_running
from tests.testcase import TestCase


class TestEnsureNoConsulRunning(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.run_command_print_ready = self.set_up_patch(
            'raptiformica.actions.mesh.run_command_print_ready'
        )

    def test_ensure_no_consul_running_logs_stopping_any_consul_agent_message(self):
        ensure_no_consul_running()

        self.log.info.assert_called_once_with(ANY)

    def test_ensure_no_consul_running_kills_any_running_consul_agents(self):
        ensure_no_consul_running()

        expected_command = "pkill -f '[c]onsul'"
        self.run_command_print_ready.assert_called_once_with(
            expected_command,
            shell=True,
            buffered=False
        )
