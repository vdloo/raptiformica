from raptiformica.actions.mesh import parse_cjdns_neighbours
from tests.testcase import TestCase


class TestParseCjdnsNeighbours(TestCase):
    def setUp(self):
        self.load_json = self.set_up_patch('raptiformica.actions.mesh.load_json')
        self.meshnet_config = {
            'cjdns': {'password': 'the_shared_secret'},
            'neighbours': {
                'a_public_key1.k': {
                    "cjdns_ipv6_address": "ipv6_address1",
                    "cjdns_public_key": "a_public_key1.k",
                    "host": "192.168.178.23",
                    "cjdns_port": 4863
                },
                'a_public_key2.k': {
                    "cjdns_ipv6_address": "ipv6_address2",
                    "cjdns_public_key": "a_public_key2.k",
                    "host": "192.168.178.24",
                    "cjdns_port": 4863
                }
            }
        }
        self.cjdroute_conf = {'publicKey': 'a_public_key3.k'}
        self.load_json.return_value = self.cjdroute_conf

    def test_parse_cjdns_neighbours_parses_all_neighbours_into_a_connectto_dict(self):
        ret = parse_cjdns_neighbours(self.meshnet_config)

        expected_neighbours = {
            '192.168.178.23:4863': {'password': 'the_shared_secret',
                                    'peerName': '192.168.178.23:4863',
                                    'publicKey': 'a_public_key1.k'},
            '192.168.178.24:4863': {'password': 'the_shared_secret',
                                    'peerName': '192.168.178.24:4863',
                                    'publicKey': 'a_public_key2.k'}
        }
        self.assertEqual(ret, expected_neighbours)

    def test_parse_cjdns_neighbours_skips_self(self):
        cjdroute_conf = {'publicKey': 'a_public_key2.k'}
        self.load_json.return_value = cjdroute_conf

        ret = parse_cjdns_neighbours(self.meshnet_config)

        expected_neighbours = {
            '192.168.178.23:4863': {'password': 'the_shared_secret',
                                    'peerName': '192.168.178.23:4863',
                                    'publicKey': 'a_public_key1.k'}
        }

        self.assertEqual(ret, expected_neighbours)
