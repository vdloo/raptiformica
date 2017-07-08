from contextlib import suppress

from mock import Mock

from raptiformica.shell.execute import terminate_and_kill
from tests.testcase import TestCase


class TestTerminateAndKill(TestCase):
    def setUp(self):
        self.process = Mock()

    def test_terminate_and_kill_terminates_process(self):
        with suppress(TimeoutError):
            terminate_and_kill(self.process, 10, "sleep 1000")
            self.process.terminate.assert_called_once_with()

    def test_terminate_and_kill_kills_process(self):
        with suppress(TimeoutError):
            terminate_and_kill(self.process, 10, "sleep 1000")
            self.process.kill.assert_called_once_with()

    def test_terminate_and_kill_raises_timeout_error(self):
        with self.assertRaises(TimeoutError):
            terminate_and_kill(self.process, 10, "sleep 1000")
