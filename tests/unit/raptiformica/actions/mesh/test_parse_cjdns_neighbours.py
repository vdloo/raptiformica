from raptiformica.actions.mesh import parse_cjdns_neighbours
from tests.testcase import TestCase


class TestParseCjdnsNeighbours(TestCase):
    def setUp(self):
        self.mapping = {
            "raptiformica/meshnet/cjdns/password": "a_secret",
            "raptiformica/meshnet/consul/password": "a_different_secret",
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_ipv6_address": "some_ipv6_address",
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_port": 4863,
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_public_key": "a_pubkey.k",
            "raptiformica/meshnet/neighbours/a_pubkey.k/host": "192.168.178.23",
            "raptiformica/meshnet/neighbours/a_pubkey.k/ssh_port": "2200",
            "raptiformica/meshnet/neighbours/a_pubkey.k/uuid": "eb442c6170694b12b277c9e88d714cf2",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_ipv6_address": "some_other_ipv6_address",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_port": 4863,
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_public_key": "a_different_pubkey.k",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/host": "192.168.178.24",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/ssh_port": "2201",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/uuid": "eb442c6170694b12b277c9e88d714cf1",
        }
        self.load_json = self.set_up_patch('raptiformica.actions.mesh.load_json')
        self.cjdroute_conf = {'publicKey': 'a_public_key3.k'}
        self.load_json.return_value = self.cjdroute_conf

    def test_parse_cjdns_config_parses_all_neighbours_from_mapping(self):
        ret = parse_cjdns_neighbours(self.mapping)

        expected_neighbours = {
            '192.168.178.23:4863': {'password': 'a_secret',
                                    'peerName': '192.168.178.23:4863',
                                    'publicKey': 'a_pubkey.k'},
            '192.168.178.24:4863': {'password': 'a_secret',
                                    'peerName': '192.168.178.24:4863',
                                    'publicKey': 'a_different_pubkey.k'}
        }
        self.assertEqual(ret, expected_neighbours)

    def test_parse_cjdns_neighbours_skips_self(self):
        cjdroute_conf = {'publicKey': 'a_pubkey.k'}
        self.load_json.return_value = cjdroute_conf

        ret = parse_cjdns_neighbours(self.mapping)

        expected_neighbours = {
            '192.168.178.24:4863': {'password': 'a_secret',
                                    'peerName': '192.168.178.24:4863',
                                    'publicKey': 'a_different_pubkey.k'}
        }

        self.assertEqual(ret, expected_neighbours)
