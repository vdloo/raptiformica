from unittest.mock import ANY

from mock import call
from itertools import chain

from raptiformica.actions.mesh import join_consul_neighbours, get_neighbour_hosts, try_run_consul_join
from tests.testcase import TestCase


class TestJoinConsulNeighbours(TestCase):
    def setUp(self):
        self.mapping = {
            "raptiformica/meshnet/cjdns/password": "a_secret",
            "raptiformica/meshnet/consul/password": "a_different_secret",
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_ipv6_address": "some_ipv6_address",
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_port": 4863,
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_public_key": "a_pubkey.k",
            "raptiformica/meshnet/neighbours/a_pubkey.k/host": "127.0.0.1",
            "raptiformica/meshnet/neighbours/a_pubkey.k/ssh_port": "2200",
            "raptiformica/meshnet/neighbours/a_pubkey.k/uuid": "eb442c6170694b12b277c9e88d714cf2",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_ipv6_address": "some_other_ipv6_address",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_port": 4863,
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_public_key": "a_different_pubkey.k",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/host": "127.0.0.1",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/ssh_port": "2201",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/uuid": "eb442c6170694b12b277c9e88d714cf1",
        }
        self.get_neighbour_hosts = self.set_up_patch(
            'raptiformica.actions.mesh.get_neighbour_hosts'
        )
        self.shuffle = self.set_up_patch(
            'raptiformica.actions.mesh.shuffle'
        )
        self.not_already_known_consul_neighbour = self.set_up_patch(
            'raptiformica.actions.mesh.not_already_known_consul_neighbour'
        )
        self.not_already_known_consul_neighbour.return_value = True
        self.get_neighbour_hosts.side_effect = get_neighbour_hosts
        self.try_run_consul_join = self.set_up_patch(
            'raptiformica.actions.mesh.try_run_consul_join'
        )

    def test_join_consul_neighbours_gets_neighbour_hosts(self):
        join_consul_neighbours(self.mapping)

        self.get_neighbour_hosts.assert_called_once_with(self.mapping)

    def test_join_consul_neighbours_randomizes_peer_join_order(self):
        join_consul_neighbours(self.mapping)

        self.assertCountEqual(
            ('some_ipv6_address', 'some_other_ipv6_address'),
            sorted(self.shuffle.call_args[0][0])
        )

    def test_join_consul_neighbours_checks_each_neighbour_for_already_known(self):
        join_consul_neighbours(self.mapping)

        expected_calls = (
            call('some_ipv6_address'),
            call('some_other_ipv6_address')
        )
        self.assertCountEqual(
            self.not_already_known_consul_neighbour.mock_calls, expected_calls
        )

    def test_join_consul_neighbours_runs_consul_join_using_the_known_neighbours_ipv6_addresses(self):
        join_consul_neighbours(self.mapping)

        self.try_run_consul_join.has_calls(
            [call('some_ipv6_address'), call('some_other_ipv6_address')]
        )

    def test_join_consul_neighbours_does_not_join_any_consul_agents_if_no_known_neighbours(self):
        join_consul_neighbours(dict())

        self.assertFalse(self.try_run_consul_join.called)

    def test_join_consul_neighbours_does_not_join_neighbours_that_are_already_known(self):
        def pretend_some_ipv6_address_is_already_known(ipv6):
            return ipv6 != 'some_ipv6_address'

        self.not_already_known_consul_neighbour.side_effect = pretend_some_ipv6_address_is_already_known
        join_consul_neighbours(self.mapping)

        try_run_consul_join_argument = self.try_run_consul_join.call_args[0][0]
        self.assertNotIn('some_ipv6_address', try_run_consul_join_argument)
        self.assertIn('some_other_ipv6_address', try_run_consul_join_argument)

    def test_join_consul_neighbours_joins_neighbours_in_batches(self):
        for address_number in range(9):
            ipv6_address_key = 'raptiformica/meshnet/neighbours/' \
                               'neighbour_key_{}.k/cjdns_ipv6_address' \
                               ''.format(address_number)
            self.mapping[ipv6_address_key] = '::{}'.format(address_number)

        join_consul_neighbours(self.mapping)

        join_ipv6_addresses = list(chain.from_iterable(
            map(lambda call_arg: call_arg[0][0], self.try_run_consul_join.call_args_list)
        ))

        self.assertEqual(self.try_run_consul_join.call_count, 11)
        expected_ipv6_addresses = list(map('::{}'.format, range(9)))
        expected_ipv6_addresses.append('some_ipv6_address')
        expected_ipv6_addresses.append('some_other_ipv6_address')
        self.assertCountEqual(expected_ipv6_addresses, join_ipv6_addresses)

    def test_join_consul_neighbours_joins_neighbours_concurrently(self):
        threadpool = self.set_up_patch('raptiformica.actions.mesh.ThreadPool')

        join_consul_neighbours(self.mapping)

        # Use ncpu amount of cores
        threadpool.assert_called_once_with()
        expected_calls = [call(try_run_consul_join, ANY)] * 3
        threadpool.return_value.apply_async.has_calls(expected_calls)
        # Close the pool after queueing all calls
        threadpool.return_value.close.assert_called_once_with()
        # Wait for all calls to be completed
        threadpool.return_value.join.assert_called_once_with()
