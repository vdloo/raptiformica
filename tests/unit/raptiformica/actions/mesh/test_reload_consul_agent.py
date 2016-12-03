from mock import ANY

from raptiformica.actions.mesh import reload_consul_agent
from tests.testcase import TestCase


class TestReloadConsulAgent(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.run_command_print_ready = self.set_up_patch(
            'raptiformica.actions.mesh.run_command_print_ready'
        )

    def test_reload_consul_agent_logs_reloading_consul_agent_message(self):
        reload_consul_agent()

        self.log.info.assert_called_once_with(ANY)

    def test_reload_consul_agent_runs_consul_reload_command(self):
        reload_consul_agent()

        expected_command = 'consul reload'
        self.run_command_print_ready.assert_called_once_with(
            expected_command,
            shell=True,
            buffered=False
        )
