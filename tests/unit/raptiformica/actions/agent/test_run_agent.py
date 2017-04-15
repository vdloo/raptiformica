from mock import call

from raptiformica.actions.agent import run_agent
from tests.testcase import TestCase


class TestRunAgent(TestCase):
    def setUp(self):
        self.attempt_join_meshnet = self.set_up_patch(
            'raptiformica.actions.agent.attempt_join_meshnet'
        )
        self.attempt_join_meshnet.side_effect = [None, RuntimeError]
        self.sleep = self.set_up_patch(
            'raptiformica.actions.agent.sleep'
        )

    def test_run_agent_joins_meshnet_until_loop_terminates(self):
        with self.assertRaises(RuntimeError):
            run_agent()

        expected_calls = (
            call(), call()
        )
        self.assertCountEqual(
            self.attempt_join_meshnet.mock_calls, expected_calls
        )

    def test_run_agent_sleeps_between_rejoins(self):
        with self.assertRaises(RuntimeError):
            run_agent()

        self.sleep.assert_called_once_with(30)

