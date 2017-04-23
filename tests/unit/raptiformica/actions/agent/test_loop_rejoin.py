from mock import call

from raptiformica.actions.agent import loop_rejoin
from tests.testcase import TestCase


class TestLoopRejoin(TestCase):
    def setUp(self):
        self.attempt_join_meshnet = self.set_up_patch(
            'raptiformica.actions.agent.attempt_join_meshnet'
        )
        self.attempt_join_meshnet.side_effect = [None, RuntimeError]
        self.sleep = self.set_up_patch(
            'raptiformica.actions.agent.sleep'
        )

    def test_loop_rejoin_joins_meshnet_until_loop_terminates(self):
        with self.assertRaises(RuntimeError):
            loop_rejoin()

        expected_calls = (
            call(), call()
        )
        self.assertCountEqual(
            self.attempt_join_meshnet.mock_calls, expected_calls
        )

    def test_loop_rejoin_sleeps_between_rejoins(self):
        with self.assertRaises(RuntimeError):
            loop_rejoin()

        self.sleep.assert_called_once_with(30)

