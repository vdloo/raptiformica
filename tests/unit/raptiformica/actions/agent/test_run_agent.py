from raptiformica.actions.agent import run_agent
from tests.testcase import TestCase


class TestRunAgent(TestCase):
    def setUp(self):
        self.agent_already_running = self.set_up_patch(
            'raptiformica.actions.agent.agent_already_running'
        )
        self.agent_already_running.return_value = True
        self.loop_rejoin = self.set_up_patch(
            'raptiformica.actions.agent.loop_rejoin'
        )

    def test_run_agent_checks_if_agent_is_already_running(self):
        run_agent()

        self.agent_already_running.assert_called_once_with()

    def test_run_agent_does_not_loop_rejoin_if_already_ruunning(self):
        run_agent()

        self.assertFalse(self.loop_rejoin.called)

    def test_run_agent_loops_rejoin_if_not_already_running(self):
        self.agent_already_running.return_value = False

        run_agent()

        self.loop_rejoin.assert_called_once_with()
