from mock import ANY

from raptiformica.actions.mesh import run_consul_join
from tests.testcase import TestCase


class TestRunConsulJoin(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.log_failure_factory = self.set_up_patch(
            'raptiformica.actions.mesh.log_failure_factory'
        )
        self.run_command_print_ready = self.set_up_patch(
            'raptiformica.actions.mesh.run_command_print_ready'
        )
        self.ipv6_addresses = ['some_ipv6_address', 'some_other_ipv6_address']

    def test_run_consul_join_logs_running_consul_join_message(self):
        run_consul_join(self.ipv6_addresses)

        self.log.info.assert_called_once_with(ANY)

    def test_run_consul_join_runs_consul_join_command(self):
        run_consul_join(self.ipv6_addresses)

        self.log_failure_factory.assert_called_once_with(ANY)
        expected_command = 'consul join [some_ipv6_address]:8301 [some_other_ipv6_address]:8301 '
        self.run_command_print_ready.assert_called_once_with(
            expected_command,
            failure_callback=self.log_failure_factory.return_value,
            shell=True,
            buffered=False
        )

