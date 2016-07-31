from raptiformica.actions.mesh import join_meshnet
from tests.testcase import TestCase


class TestJoinMeshnet(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.config = {
            'meshnet': {
                'neighbours': {
                    'a_public_key1.k': {
                        "cjdns_ipv6_address": "ipv6_address1",
                        "cjdns_public_key": "a_public_key1.k",
                        "host": "192.168.178.23",
                        "port": 4863
                    },
                    'a_public_key2.k': {
                        "cjdns_ipv6_address": "ipv6_address2",
                        "cjdns_public_key": "a_public_key2.k",
                        "host": "192.168.178.24",
                        "port": 4863
                    }
                }
            }
        }
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_join_meshnet_logs_joining_meshnet_message(self):
        join_meshnet(self.config)

        self.assertTrue(self.log.info.called)

    def test_join_meshnet_runs_join_command(self):
        join_meshnet(self.config)

        expected_command = "sleep 5; consul join [ipv6_address1]:8301 [ipv6_address2]:8301 "
        self.execute_process.assert_called_once_with(
            expected_command,
            shell=True,
            buffered=False
        )

    def test_join_meshnet_raises_error_when_running_the_join_command_failed(self):
        process_output = (1, 'standard out output', 'standard error output')
        self.execute_process.return_value = process_output

        with self.assertRaises(RuntimeError):
            join_meshnet(self.config)

