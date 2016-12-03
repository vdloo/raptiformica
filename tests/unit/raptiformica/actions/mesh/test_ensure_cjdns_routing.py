from mock import ANY

from raptiformica.actions.mesh import ensure_cjdns_routing
from tests.testcase import TestCase


class TestEnsureCjdnsRouting(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.stop_detached_cjdroute = self.set_up_patch(
            'raptiformica.actions.mesh.stop_detached_cjdroute'
        )
        self.start_detached_cjdroute = self.set_up_patch(
            'raptiformica.actions.mesh.start_detached_cjdroute'
        )
        self.block_until_tun0_becomes_available = self.set_up_patch(
            'raptiformica.actions.mesh.block_until_tun0_becomes_available'
        )
        self.ensure_ipv6_routing = self.set_up_patch(
            'raptiformica.actions.mesh.ensure_ipv6_routing'
        )

    def test_ensure_cjdns_routing_logs_ensuring_cjdns_routing_message(self):
        ensure_cjdns_routing()

        self.log.info.assert_called_once_with(ANY)

    def test_ensure_cjdns_routing_stops_detached_cjdroute(self):
        ensure_cjdns_routing()

        self.stop_detached_cjdroute.assert_called_once_with()

    def test_ensure_cjdns_routing_starts_detached_cjdroute(self):
        ensure_cjdns_routing()

        self.start_detached_cjdroute.assert_called_once_with()

    def test_ensure_cjdns_routing_blocks_until_tun0_becomes_available(self):
        ensure_cjdns_routing()

        self.block_until_tun0_becomes_available.assert_called_once_with()

    def test_ensure_cjdns_routing_ensure_ipv6_routing(self):
        ensure_cjdns_routing()

        self.ensure_ipv6_routing.assert_called_once_with()

