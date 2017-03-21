from mock import ANY
from tests.testcase import TestCase

from socket import  AF_INET, SOCK_STREAM
from raptiformica.distributed.ping import check_port_open


class TestCheckPortOpen(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.distributed.ping.log'
        )
        self.socket = self.set_up_patch(
            'raptiformica.distributed.ping.socket'
        )

    def test_check_port_open_logs_to_debug(self):
        check_port_open('127.0.0.1', port=22)

        self.log.debug.assert_called_once_with(ANY)

    def test_check_port_open_instantiates_socket(self):
        check_port_open('127.0.0.1', port=22)

        self.socket.assert_called_once_with(
            AF_INET, SOCK_STREAM
        )

    def test_check_port_open_connects_to_port(self):
        check_port_open('127.0.0.1', port=22)

        self.socket.return_value.connect_ex.assert_called_once_with(
            ('127.0.0.1', 22)
        )

    def test_check_port_open_closes_socket(self):
        check_port_open('127.0.0.1', port=22)

        self.socket.return_value.close.assert_called_once_with()

    def test_check_port_open_returns_true_if_port_open(self):
        self.socket.return_value.connect_ex.return_value = 0

        ret = check_port_open('127.0.0.1', port=22)

        self.assertTrue(ret)

    def test_check_port_open_returns_false_if_port_is_not_open(self):
        self.socket.return_value.connect_ex.return_value = 1

        ret = check_port_open('127.0.0.1', port=22)

        self.assertFalse(ret)
