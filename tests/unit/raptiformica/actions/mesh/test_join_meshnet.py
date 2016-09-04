from raptiformica.actions.mesh import join_meshnet
from tests.testcase import TestCase


class TestJoinMeshnet(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output
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
        self.get_config = self.set_up_patch('raptiformica.actions.mesh.get_config')
        self.get_config.return_value = self.mapping

    def test_join_meshnet_logs_joining_meshnet_message(self):
        join_meshnet()

        self.assertTrue(self.log.info.called)

    def test_join_meshnet_runs_join_command(self):
        join_meshnet()

        expected_command = "sleep 5; consul join [some_ipv6_address]:8301 [some_other_ipv6_address]:8301 "
        self.execute_process.assert_called_once_with(
            expected_command,
            shell=True,
            buffered=False
        )

    def test_join_meshnet_raises_error_when_running_the_join_command_failed(self):
        process_output = (1, 'standard out output', 'standard error output')
        self.execute_process.return_value = process_output

        with self.assertRaises(RuntimeError):
            join_meshnet()

