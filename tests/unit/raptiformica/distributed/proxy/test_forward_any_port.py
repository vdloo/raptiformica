from mock import Mock

import raptiformica.distributed.proxy
from tests.testcase import TestCase


class TestForwardAnyPort(TestCase):
    def setUp(self):
        self.forward_remote_port = self.set_up_patch(
            'raptiformica.distributed.proxy.forward_remote_port'
        )
        self.forward_remote_port.return_value.__exit__ = Mock()
        self.forward_remote_port.return_value.__enter__ = Mock()
        self.host_and_port_pairs_from_config = self.set_up_patch(
            'raptiformica.distributed.discovery.host_and_port_pairs_from_config'
        )
        self.try_machine_command = self.set_up_patch(
            'raptiformica.distributed.proxy.try_machine_command'
        )
        self.try_machine_command.return_value = (0, '1.2.3.4', 1122)

    def test_forward_any_port_gets_cached_host_and_port_pairs(self):
        with raptiformica.distributed.proxy.forward_any_port(8500):
            pass

        self.host_and_port_pairs_from_config.assert_called_once_with(
            cached=True
        )

    def test_forward_any_port_tries_finding_eligible_neighbour_one_time(self):
        with raptiformica.distributed.proxy.forward_any_port(8500):
            pass

        self.try_machine_command.assert_called_once_with(
            self.host_and_port_pairs_from_config.return_value,
            ['/bin/true'],
            attempt_limit=1
        )

    def test_forward_any_port_tries_finding_eligible_neighbour_with_specified_predicate(self):
        with raptiformica.distributed.proxy.forward_any_port(
            8500, predicate=['consul', 'members']
        ):
            pass

        self.try_machine_command.assert_called_once_with(
                self.host_and_port_pairs_from_config.return_value,
                ['consul', 'members'],
                attempt_limit=1
        )

    def test_forward_any_port_raises_error_if_no_eligible_host_found(self):
        self.try_machine_command.return_value = (None, None, None)

        with self.assertRaises(RuntimeError):
            with raptiformica.distributed.proxy.forward_any_port(8500):
                pass

    def test_forward_any_port_forwards_remote_port_in_context(self):
        self.assertFalse(self.forward_remote_port.return_value.__enter__.called)
        self.assertFalse(self.forward_remote_port.return_value.__exit__.called)

        with raptiformica.distributed.proxy.forward_any_port(8500):
            self.assertTrue(self.forward_remote_port.return_value.__enter__.called)
            self.assertFalse(self.forward_remote_port.return_value.__exit__.called)

        self.assertTrue(self.forward_remote_port.return_value.__exit__.called)
