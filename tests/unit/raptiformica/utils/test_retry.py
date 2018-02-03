from unittest.mock import Mock

from raptiformica.utils import retry
from tests.testcase import TestCase


class TestRetry(TestCase):
    def setUp(self):
        self.sleep = self.set_up_patch('raptiformica.utils.sleep')

    def test_retry_does_not_retry_function_if_no_exception(self):
        fake_function = Mock()

        @retry(attempts=2, expect=(RuntimeError,))
        def func():
            return fake_function()

        ret = func()

        fake_function.assert_called_once_with()
        self.assertEqual(ret, fake_function.return_value)

    def test_retry_does_not_retry_function_if_unexpected_exception(self):
        fake_function = Mock()
        fake_function.side_effect = TimeoutError

        @retry(attempts=2, expect=(RuntimeError,))
        def func():
            fake_function()

        with self.assertRaises(TimeoutError):
            func()

    def test_retry_retries_function_if_expected_exception(self):
        fake_function = Mock()
        fake_function.side_effect = (TimeoutError, 'some output')

        @retry(attempts=2, expect=(TimeoutError,))
        def func():
            return fake_function()

        ret = func()

        self.assertEqual(ret, 'some output')

    def test_retry_does_not_retry_function_anymore_if_retries_ran_out(self):
        fake_function = Mock()
        fake_function.side_effect = (TimeoutError, TimeoutError, None)

        @retry(attempts=2, expect=(TimeoutError,))
        def func():
            fake_function()

        with self.assertRaises(TimeoutError):
            func()

    def test_retry_does_not_sleep_if_no_exception(self):
        @retry(attempts=2)
        def func():
            pass

        func()

        self.assertFalse(self.sleep.called)

    def test_retry_sleeps_after_retry_if_retry_specified_and_expected_exception(self):
        fake_function = Mock()
        fake_function.side_effect = (TimeoutError, 'some output')

        @retry(attempts=2, expect=(TimeoutError,), wait_before_retry=5)
        def func():
            return fake_function()

        func()

        self.sleep.assert_called_once_with(5)

    def test_retry_does_not_sleep_if_retries_ran_out(self):
        fake_function = Mock()
        fake_function.side_effect = (TimeoutError, 'some output')

        @retry(attempts=1, expect=(TimeoutError,), wait_before_retry=5)
        def func():
            return fake_function()

        self.assertFalse(self.sleep.called)
