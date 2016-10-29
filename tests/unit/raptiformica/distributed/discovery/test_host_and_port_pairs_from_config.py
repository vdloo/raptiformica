from raptiformica.distributed.discovery import host_and_port_pairs_from_config
from tests.testcase import TestCase


class TestHostAndPortPairsFromConfig(TestCase):
    def setUp(self):
        self.get_config = self.set_up_patch(
            'raptiformica.settings.load.get_config_mapping'
        )
        self.mapping = {
            "raptiformica/meshnet/neighbours/public_key_1.k/cjdns_ipv6_address": "1:2:3:4",
            "raptiformica/meshnet/neighbours/public_key_1.k/cjdns_port": "4863",
            "raptiformica/meshnet/neighbours/public_key_1.k/cjdns_public_key": "public_key_1.k",
            "raptiformica/meshnet/neighbours/public_key_1.k/host": "172.17.0.6",
            "raptiformica/meshnet/neighbours/public_key_1.k/ssh_port": "22",
            "raptiformica/meshnet/neighbours/public_key_1.k/uuid": "1",
            "raptiformica/meshnet/neighbours/public_key_2.k/cjdns_ipv6_address": "1:2:3:5",
            "raptiformica/meshnet/neighbours/public_key_2.k/cjdns_port": "4863",
            "raptiformica/meshnet/neighbours/public_key_2.k/cjdns_public_key": "public_key_2.k",
            "raptiformica/meshnet/neighbours/public_key_2.k/host": "172.17.0.7",
            "raptiformica/meshnet/neighbours/public_key_2.k/ssh_port": "22",
            "raptiformica/meshnet/neighbours/public_key_2.k/uuid": "2",
            "raptiformica/meshnet/neighbours/public_key_3.k/cjdns_ipv6_address": "1:2:3:6",
            "raptiformica/meshnet/neighbours/public_key_3.k/cjdns_port": "4863",
            "raptiformica/meshnet/neighbours/public_key_3.k/cjdns_public_key": "public_key_3.k",
            "raptiformica/meshnet/neighbours/public_key_3.k/host": "172.17.0.8",
            "raptiformica/meshnet/neighbours/public_key_3.k/ssh_port": "22",
            "raptiformica/meshnet/neighbours/public_key_3.k/uuid": "3",
        }
        self.get_config.return_value = self.mapping

    def test_host_and_port_pairs_from_config_gets_pairs(self):
        ret = host_and_port_pairs_from_config()

        expected_pairs = [
            ('172.17.0.8', '22'),
            ('172.17.0.7', '22'),
            ('172.17.0.6', '22')
        ]
        self.assertCountEqual(ret, expected_pairs)

    def test_host_and_port_pairs_from_config_returns_empty_list_if_no_neighbours(self):
        self.mapping = {
            "raptiformica/meshnet/": None,
        }
        self.get_config.return_value = self.mapping

        ret = host_and_port_pairs_from_config()

        self.assertCountEqual(ret, tuple())

    def test_host_and_port_pairs_from_config_returns_empty_list_if_no_meshnet_config(self):
        self.mapping = {'raptiformica/': None}
        self.get_config.return_value = self.mapping

        ret = host_and_port_pairs_from_config()

        self.assertCountEqual(ret, tuple())
