from mock import ANY

from raptiformica.distributed.ping import find_host_that_can_ping
from tests.testcase import TestCase


class TestFindHostThatCanPing(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.distributed.ping.log'
        )
        self.host_and_port_pairs_from_config = self.set_up_patch(
            'raptiformica.distributed.ping.host_and_port_pairs_from_config'
        )
        self.try_ping = self.set_up_patch(
            'raptiformica.distributed.ping.try_ping'
        )
        self.try_ping.return_value = (
            0, '1.2.3.3', 2222
        )

    def test_find_host_that_can_ping_logs_finding_host_that_can_ping_message(self):
        find_host_that_can_ping('1.2.3.4')

        self.log.info.assert_called_once_with(ANY)

    def test_find_host_that_can_ping_gets_host_and_port_pairs_from_config(self):
        find_host_that_can_ping('1.2.3.4')

        self.host_and_port_pairs_from_config.assert_called_once_with()

    def test_find_host_that_can_ping_tries_pinging_the_host_from_the_config_neighbours(self):
        find_host_that_can_ping('1.2.3.4')

        self.try_ping.assert_called_once_with(
            self.host_and_port_pairs_from_config.return_value,
            '1.2.3.4'
        )

    def test_find_host_that_can_ping_returns_access_host(self):
        host, _ = find_host_that_can_ping('1.2.3.4')

        self.assertEqual(host, '1.2.3.3')

    def test_find_host_that_can_ping_returns_access_host_ssh_port(self):
        _, port = find_host_that_can_ping('1.2.3.4')

        self.assertEqual(port, 2222)
