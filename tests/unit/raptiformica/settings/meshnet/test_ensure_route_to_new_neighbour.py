from raptiformica.settings.meshnet import ensure_route_to_new_neighbour
from tests.testcase import TestCase


class TestEnsureRouteToNewNeighbour(TestCase):
    def setUp(self):
        self.update_meshnet_config = self.set_up_patch(
            'raptiformica.settings.meshnet.update_meshnet_config'
        )
        self.find_host_that_can_ping = self.set_up_patch(
            'raptiformica.settings.meshnet.find_host_that_can_ping'
        )
        self.find_host_that_can_ping.return_value = ('1.2.3.3', 22)
        self.bootstrap_host_to_neighbour = self.set_up_patch(
            'raptiformica.settings.meshnet.bootstrap_host_to_neighbour'
        )
        self.send_reload_meshnet = self.set_up_patch(
            'raptiformica.settings.meshnet.send_reload_meshnet'
        )

    def test_ensure_route_to_new_neighbour_updates_meshnet_config(self):
        ensure_route_to_new_neighbour('1.2.3.4', port=2222)

        self.update_meshnet_config.assert_called_once_with(
            '1.2.3.4', port=2222, compute_checkout_uuid=None
        )

    def test_ensure_route_to_new_neighbour_updates_meshnet_config_with_compute_checkout_uuid(self):
        ensure_route_to_new_neighbour('1.2.3.4', port=2222, compute_checkout_uuid='1234-1234-1234-1234')

        self.update_meshnet_config.assert_called_once_with(
            '1.2.3.4', port=2222, compute_checkout_uuid='1234-1234-1234-1234'
        )

    def test_ensure_route_to_new_neighbour_finds_host_that_can_ping_the_specified_host(self):
        ensure_route_to_new_neighbour('1.2.3.4', port=2222)

        self.find_host_that_can_ping.assert_called_once_with(
            '1.2.3.4'
        )

    def test_ensure_route_to_new_neighbour_bootstraps_host_to_neighbour_if_connected_neighbour(self):
        ensure_route_to_new_neighbour('1.2.3.4', port=2222)

        self.bootstrap_host_to_neighbour.assert_called_once_with(
            '1.2.3.4', 2222, '1.2.3.3', 22
        )

    def test_ensure_route_to_new_neighbour_does_not_bootstrap_host_to_neighbour_if_no_connected_neighbour(self):
        self.find_host_that_can_ping.return_value = (None, None)

        ensure_route_to_new_neighbour('1.2.3.4', port=2222)

        self.assertFalse(self.bootstrap_host_to_neighbour.called)

    def test_ensure_route_to_new_neighbour_sends_reload_meshnet(self):
        ensure_route_to_new_neighbour('1.2.3.4', port=2222)

        self.send_reload_meshnet.assert_called_once_with()
