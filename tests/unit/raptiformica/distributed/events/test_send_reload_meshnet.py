from mock import ANY

from raptiformica.distributed.events import send_reload_meshnet
from tests.testcase import TestCase


class TestSendReloadMeshnet(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.distributed.events.log'
        )
        self.host_and_port_pairs_from_config = self.set_up_patch(
            'raptiformica.distributed.events.host_and_port_pairs_from_config'
        )
        self.try_send_consul_event = self.set_up_patch(
            'raptiformica.distributed.events.try_send_consul_event'
        )

    def test_send_reload_meshnet_logs_sending_reload_message(self):
        send_reload_meshnet()

        self.log.info.assert_called_once_with(ANY)

    def test_send_reload_meshnet_gets_host_and_port_pairs_from_config(self):
        send_reload_meshnet()

        self.host_and_port_pairs_from_config.assert_called_once_with()

    def test_send_reload_meshnet_tries_sending_notify_cluster_change_event(self):
        send_reload_meshnet()

        self.try_send_consul_event.assert_called_once_with(
            self.host_and_port_pairs_from_config.return_value,
            'notify_cluster_change'
        )
