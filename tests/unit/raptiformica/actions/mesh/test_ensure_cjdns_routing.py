from mock import ANY

from raptiformica.actions.mesh import ensure_cjdns_routing
from tests.testcase import TestCase


class TestEnsureCjdnsRouting(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.cjdroute_config_hash_outdated = self.set_up_patch(
            'raptiformica.actions.mesh.cjdroute_config_hash_outdated'
        )
        self.check_if_tun0_is_available = self.set_up_patch(
            'raptiformica.actions.mesh.check_if_tun0_is_available'
        )
        self.stop_detached_cjdroute = self.set_up_patch(
            'raptiformica.actions.mesh.stop_detached_cjdroute'
        )
        self.block_until_cjdroute_port_is_free = self.set_up_patch(
            'raptiformica.actions.mesh.block_until_cjdroute_port_is_free'
        )
        self.start_detached_cjdroute = self.set_up_patch(
            'raptiformica.actions.mesh.start_detached_cjdroute'
        )
        self.write_cjdroute_config_hash = self.set_up_patch(
            'raptiformica.actions.mesh.write_cjdroute_config_hash'
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

    def test_ensure_cjdns_routing_checks_if_cjdroute_config_hash_is_outdated(self):
        ensure_cjdns_routing()

        self.cjdroute_config_hash_outdated.assert_called_once_with()

    def test_ensure_cjdns_routing_does_not_check_if_tun0_is_available_if_cjdroute_config_hash_is_outdated(self):
        self.cjdroute_config_hash_outdated.return_value = True

        ensure_cjdns_routing()

        # We do not have to check the tun0 device. Checking the device is 'slow'
        # compared to checking the config hash file. If we already know that the
        # config file hash is no longer up to date with the config on disk then
        # we need to (re)start the cjdns agent anyway so we skip the
        # check_if_tun0_is_available check using the 'or' short-circuit evaluation
        self.assertFalse(self.check_if_tun0_is_available.called)

    def test_ensure_cjdns_routing_checks_if_tun0_is_available_if_cjdroute_config_is_up_to_date(self):
        self.cjdroute_config_hash_outdated.return_value = False

        ensure_cjdns_routing()

        # If the config hash is up to date it means that the last started cjdroute
        # used a config that is still up to date. However it does not mean that the
        # daemon is still running (or is frozen). If we can't see the tun0 device we
        # need to (re)start cjdroute.
        self.check_if_tun0_is_available.assert_called_once_with()

    def test_ensure_cjdns_routing_stops_detached_cjdroute_if_config_hash_up_to_date_and_tun0_available(self):
        self.cjdroute_config_hash_outdated.return_value = True

        ensure_cjdns_routing()

        self.stop_detached_cjdroute.assert_called_once_with()

    def test_ensure_cjdns_routing_blocks_until_cjdroute_port_is_free(self):
        self.cjdroute_config_hash_outdated.return_value = True

        ensure_cjdns_routing()

        self.block_until_cjdroute_port_is_free.assert_called_once_with()

    def test_ensure_cjdns_routing_starts_detached_cjdroute_if_config_hash_up_to_date_and_tun0_available(self):
        self.cjdroute_config_hash_outdated.return_value = True

        ensure_cjdns_routing()

        self.start_detached_cjdroute.assert_called_once_with()

    def test_ensure_cjdns_routing_blocks_until_tun0_becomes_available_if_config_hash_up_to_date_and_tun0_available(self):
        self.cjdroute_config_hash_outdated.return_value = True

        ensure_cjdns_routing()

        self.block_until_tun0_becomes_available.assert_called_once_with()

    def test_ensure_cjdns_routing_ensures_ipv6_routing_if_config_hash_up_to_date_and_tun0_available(self):
        self.cjdroute_config_hash_outdated.return_value = True

        ensure_cjdns_routing()

        self.ensure_ipv6_routing.assert_called_once_with()

    def test_ensure_cjdns_routing_writes_cjdroute_config_hash_if_config_hash_up_to_date_and_tun0_available(self):
        self.cjdroute_config_hash_outdated.return_value = True

        ensure_cjdns_routing()

        self.write_cjdroute_config_hash.assert_called_once_with()

    def test_ensure_cjdns_routing_stops_detached_cjdroute_if_tun0_not_available(self):
        self.cjdroute_config_hash_outdated.return_value = False
        self.check_if_tun0_is_available.return_value = False

        ensure_cjdns_routing()

        self.stop_detached_cjdroute.assert_called_once_with()

    def test_ensure_cjdns_routing_blocks_until_cjdroute_port_is_free_if_tun0_not_available(self):
        self.cjdroute_config_hash_outdated.return_value = False
        self.check_if_tun0_is_available.return_value = False

        ensure_cjdns_routing()

        self.block_until_cjdroute_port_is_free.assert_called_once_with()

    def test_ensure_cjdns_routing_starts_detached_cjdroute_if_tun0_not_available(self):
        self.cjdroute_config_hash_outdated.return_value = False
        self.check_if_tun0_is_available.return_value = False

        ensure_cjdns_routing()

        self.start_detached_cjdroute.assert_called_once_with()

    def test_ensure_cjdns_routing_blocks_until_tun0_becomes_available_if_tun0_not_available(self):
        self.cjdroute_config_hash_outdated.return_value = False
        self.check_if_tun0_is_available.return_value = False

        ensure_cjdns_routing()

        self.block_until_tun0_becomes_available.assert_called_once_with()

    def test_ensure_cjdns_routing_ensures_ipv6_routing_if_tun0_not_available(self):
        self.cjdroute_config_hash_outdated.return_value = False
        self.check_if_tun0_is_available.return_value = False

        ensure_cjdns_routing()

        self.ensure_ipv6_routing.assert_called_once_with()

    def test_ensure_cjdns_routing_writes_cjdroute_config_hash_if_tun0_not_available(self):
        self.cjdroute_config_hash_outdated.return_value = False
        self.check_if_tun0_is_available.return_value = False

        ensure_cjdns_routing()

        self.write_cjdroute_config_hash.assert_called_once_with()

    def test_ensure_cjdns_routing_does_not_stop_detached_cjdroute_if_config_hash_up_to_date_and_tun0_available(self):
        self.cjdroute_config_hash_outdated.return_value = False
        self.check_if_tun0_is_available.return_value = True

        ensure_cjdns_routing()

        self.assertFalse(self.stop_detached_cjdroute.called)

    def test_ensure_cjdns_routing_does_not_block_until_cjdroute_port_is_free_if_config_hash_up_to_date_and_tun0(self):
        self.cjdroute_config_hash_outdated.return_value = False
        self.check_if_tun0_is_available.return_value = True

        ensure_cjdns_routing()

        self.assertFalse(self.block_until_cjdroute_port_is_free.called)

    def test_ensure_cjdns_routing_does_not_start_detached_cjdroute_if_config_hash_up_to_date_and_tun0_available(self):
        self.cjdroute_config_hash_outdated.return_value = False
        self.check_if_tun0_is_available.return_value = True

        ensure_cjdns_routing()

        self.assertFalse(self.start_detached_cjdroute.called)

    def test_ensure_cjdns_routing_does_not_block_for_tun0_if_config_hash_up_to_date_and_tun0_available(self):
        self.cjdroute_config_hash_outdated.return_value = False
        self.check_if_tun0_is_available.return_value = True

        ensure_cjdns_routing()

        self.assertFalse(self.block_until_tun0_becomes_available.called)

    def test_ensure_cjdns_routing_does_not_ensure_ipv6_routing_if_config_hash_up_to_date_and_tun0_available(self):
        self.cjdroute_config_hash_outdated.return_value = False
        self.check_if_tun0_is_available.return_value = True

        ensure_cjdns_routing()

        self.assertFalse(self.ensure_ipv6_routing.called)

    def test_ensure_cjdns_routing_does_not_write_cjdroute_config_hash_if_config_hash_up_to_date_and_tun0_available(self):
        self.cjdroute_config_hash_outdated.return_value = False
        self.check_if_tun0_is_available.return_value = True

        ensure_cjdns_routing()

        self.assertFalse(self.write_cjdroute_config_hash.called)
