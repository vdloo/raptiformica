from mock import Mock

from raptiformica.shell.execute import terminate_on_timeout, terminate_and_kill
from tests.testcase import TestCase


class TestTerminateOnTimeout(TestCase):
    def setUp(self):
        self.process = Mock()
        self.timer = self.set_up_patch(
            'raptiformica.shell.execute.Timer'
        )

    def test_terminate_on_timeout_instantiates_timer_before_context(self):
        self.assertFalse(self.timer.called)

        with terminate_on_timeout(self.process, 10, "sleep 100"):
            self.timer.assert_called_once_with(
                10, terminate_and_kill,
                args=[self.process, 10, "sleep 100"]
            )

    def test_terminate_on_timeout_starts_timer_before_context(self):
        self.assertFalse(self.timer.return_value.start.called)

        with terminate_on_timeout(self.process, 10, "sleep 100"):
            self.timer.return_value.start.assert_called_once_with()

    def test_terminate_on_timeout_cancels_timer_after_context(self):
        self.assertFalse(self.timer.return_value.cancel.called)

        with terminate_on_timeout(self.process, 10, "sleep 100"):
            self.assertFalse(self.timer.return_value.cancel.called)

        self.timer.return_value.cancel.assert_called_once_with()
