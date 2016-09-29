from mock import call
from raptiformica.utils import wait
from tests.testcase import TestCase


def predicate():
    return True


class TestWait(TestCase):
    def setUp(self):
        self.sleep = self.set_up_patch(
            'raptiformica.utils.sleep'
        )

    def test_wait_returns_immediately_if_predicate_evaluates_to_true_on_first_try(self):
        wait(predicate)

        self.assertFalse(self.sleep.called)

    def test_wait_re_polls_the_predicate_after_a_delay_until_it_evaluates_to_true(self):
        test_predicate = self.set_up_patch('tests.unit.raptiformica.utils.test_wait.predicate')
        test_predicate.side_effect = (False, False, True)

        wait(predicate)

        expected_calls = map(call, (1, 1))
        self.assertCountEqual(self.sleep.mock_calls, expected_calls)

    def test_wait_raises_timeout_error_if_took_too_long(self):
        test_predicate = self.set_up_patch('tests.unit.raptiformica.utils.test_wait.predicate')
        test_predicate.side_effect = (False, False, False, True)

        with self.assertRaises(TimeoutError):
            wait(predicate, timeout=2)
