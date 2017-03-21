from tests.testcase import TestCase
from mock import ANY

from raptiformica.actions.join import verify_local_ssh_running


class TestVerifyLocalSSHRunning(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.actions.join.log'
        )
        self.check_port_open = self.set_up_patch(
            'raptiformica.actions.join.check_port_open'
        )

    def test_verify_local_ssh_running_logs_info_message(self):
        verify_local_ssh_running()

        self.log.info.assert_called_once_with(ANY)

    def test_verify_local_ssh_running_checks_if_the_default_ssh_port_on_the_local_host_is_open(self):
        verify_local_ssh_running()

        self.check_port_open.assert_called_once_with(
            '127.0.0.1', 22
        )

    def test_verify_local_ssh_running_does_not_raise_an_error_if_the_port_is_open(self):
        self.check_port_open.return_value = True

        ret = verify_local_ssh_running()

        self.assertIsNone(ret)

    def test_verify_local_ssh_running_raises_an_error_if_the_port_is_not_open(self):
        self.check_port_open.return_value = False

        with self.assertRaises(RuntimeError):
            verify_local_ssh_running()

