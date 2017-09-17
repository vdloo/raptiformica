from mock import call

from raptiformica.actions.agent import loop_rejoin
from tests.testcase import TestCase


class TestLoopRejoin(TestCase):
    def setUp(self):
        self.attempt_join_meshnet = self.set_up_patch(
            'raptiformica.actions.agent.attempt_join_meshnet'
        )
        self.sleep = self.set_up_patch(
            'raptiformica.actions.agent.sleep'
        )
        self.sleep.side_effect = [None, IOError]

    def test_loop_rejoin_joins_meshnet_until_loop_terminates(self):
        with self.assertRaises(IOError):
            loop_rejoin()

        expected_calls = (
            call(), call()
        )
        self.assertCountEqual(
            self.attempt_join_meshnet.mock_calls, expected_calls
        )

    def test_loop_ignores_attempt_join_meshnet_exceptions(self):
        self.attempt_join_meshnet.side_effect = IOError

        with self.assertRaises(IOError):
            loop_rejoin()

        self.attempt_join_meshnet.assert_has_calls([call()] * 2)

    def test_loop_rejoin_sleeps_between_rejoins(self):
        with self.assertRaises(IOError):
            loop_rejoin()

        self.sleep.assert_has_calls([call(30)] * 2)

