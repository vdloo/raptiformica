from raptiformica.cli import agent
from tests.testcase import TestCase


class TestAgent(TestCase):
    def setUp(self):
        self.parse_agent_arguments = self.set_up_patch(
            'raptiformica.cli.parse_agent_arguments'
        )
        self.run_agent = self.set_up_patch(
            'raptiformica.cli.run_agent'
        )

    def test_agent_parses_agent_arguments(self):
        agent()

        self.parse_agent_arguments.assert_called_once_with()

    def test_agent_agentes_machine(self):
        agent()

        self.run_agent.assert_called_once_with()

