from raptiformica.distributed.events import try_send_consul_event
from tests.testcase import TestCase


class TestTrySendConsulEvent(TestCase):
    def setUp(self):
        self.try_machine_command = self.set_up_patch(
            'raptiformica.distributed.events.try_machine_command'
        )
        self.try_machine_command.return_value = ('output', '5.6.7.8', '22')
        self.host_and_port_pairs = [
            ('1.2.3.4', '2222'),
            ('5.6.7.8', '22')
        ]

    def test_try_send_consul_event_tries_machine_command(self):
        try_send_consul_event(self.host_and_port_pairs, 'notify_cluster_change')

        expected_command = ['consul', 'event', '-name=notify_cluster_change']
        self.try_machine_command.assert_called_once_with(
            self.host_and_port_pairs,
            expected_command,
            attempt_message="Trying to send notify_cluster_change event on {}:{}",
            all_failed_message="Could not send the event on any machine in the "
                               "distributed network. Maybe no meshnet has been "
                               "established yet."
        )

    def test_try_send_consul_event_returns_output_from_first_successful_sent_event(self):
        ret = try_send_consul_event(self.host_and_port_pairs, 'notify_cluster_change')

        self.assertEqual(ret, 'output')
