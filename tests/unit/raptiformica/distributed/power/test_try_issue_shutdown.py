from raptiformica.distributed.power import try_issue_shutdown
from tests.testcase import TestCase


class TestTryIssueShutdown(TestCase):
    def setUp(self):
        self.try_machine_command = self.set_up_patch('raptiformica.distributed.power.try_machine_command')
        self.try_machine_command.return_value = ('output', '5.6.7.8', '22')
        self.host_and_port_pairs = [
            ('1.2.3.4', '2222'),
            ('5.6.7.8', '22')
        ]

    def test_try_issue_shutdown_tries_machine_command(self):
        try_issue_shutdown(self.host_and_port_pairs)

        expected_command = ["consul", "exec", "'shutdown -h now'"]
        self.try_machine_command.assert_called_once_with(
            self.host_and_port_pairs,
            expected_command,
            attempt_message="Trying to issue a global shutdown on {}:{}",
            all_failed_message="Failed to issue a global shutdown on any of the nodes."
        )

    def test_try_issue_shutdown_returns_output_from_first_successful_consul_exec(self):
        ret = try_issue_shutdown(self.host_and_port_pairs)

        self.assertEqual(ret, 'output')
