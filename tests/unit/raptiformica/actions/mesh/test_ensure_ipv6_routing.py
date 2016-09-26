from mock import call
from tests.testcase import TestCase

from raptiformica.actions.mesh import ensure_ipv6_routing


class TestEnsureIPv6Routing(TestCase):
    def setUp(self):
        self.run_command_print_ready = self.set_up_patch(
            'raptiformica.actions.mesh.run_command_print_ready'
        )

    def test_ensure_ipv6_routing_runs_ip_add_command_for_all_routing_rules(self):
        ensure_ipv6_routing()

        expected_calls = (
            call('ip -6 route add fe80::/64 dev eth0  '
                 'proto kernel  metric 256  pref medium',
                 shell=True),
            call('ip -6 route add fc00::/8 dev tun0  '
                 'proto kernel  metric 256  mtu 1304 pref medium',
                 shell=True),
        )
        self.assertCountEqual(
                self.run_command_print_ready.mock_calls,
                expected_calls
        )
