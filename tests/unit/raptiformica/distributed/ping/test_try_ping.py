from raptiformica.distributed.ping import try_ping
from tests.testcase import TestCase


class TestTryPing(TestCase):
    def setUp(self):
        self.try_machine_command = self.set_up_patch(
            'raptiformica.distributed.ping.try_machine_command'
        )
        self.try_machine_command.return_value = ('output', '1.2.3.4', '2222')
        self.host_and_port_pairs = [
            ('1.2.3.4', '2222'),
            ('5.6.7.8', '22')
        ]

    def test_try_ping_tries_machine_command(self):
        try_ping(self.host_and_port_pairs, '1.2.3.4')

        expected_command = ["ping", "-c", "1", "-W", "1", '1.2.3.4']
        self.try_machine_command.assert_called_once_with(
            self.host_and_port_pairs,
            expected_command,
            attempt_message="Trying to ping 1.2.3.4 from {}:{}",
            all_failed_message="Could not ping the host on any machine in the "
                               "distributed network. Maybe no meshnet has been "
                               "established yet."
        )

    def test_try_ping_returns_output_host_and_port_of_first_successful_ping(self):
        output, success_host, success_port = try_ping(self.host_and_port_pairs, '1.2.3.4')

        self.assertEqual(output, 'output')
        self.assertEqual(success_host, '1.2.3.4')
        self.assertEqual(success_port, '2222')
