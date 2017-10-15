from mock import ANY, call

from raptiformica.actions.mesh import try_run_consul_join
from tests.testcase import TestCase


class TestTryRunConsulJoin(TestCase):
    def setUp(self):
        self.run_consul_join = self.set_up_patch(
            'raptiformica.actions.mesh.run_consul_join'
        )

    def test_try_run_consul_join_runs_consul_join(self):
        try_run_consul_join(['::1'])

        self.run_consul_join.assert_called_once_with(ipv6_addresses=['::1'])

    def test_try_run_consul_join_retries_if_command_fails(self):
        self.run_consul_join.side_effect = [RuntimeError, None]

        try_run_consul_join(['::1'])

        expected_calls = (
            call(ipv6_addresses=['::1']),
            call(ipv6_addresses=['::1'])
        )
        self.assertCountEqual(expected_calls, self.run_consul_join.mock_calls)

    def test_try_run_consul_join_does_not_catch_unspecified_exceptions(self):
        self.run_consul_join.side_effect = IOError

        with self.assertRaises(IOError):
            try_run_consul_join(['::1'])
