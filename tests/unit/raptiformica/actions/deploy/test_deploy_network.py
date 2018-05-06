from mock import call

from raptiformica.actions.deploy import deploy_network
from tests.testcase import TestCase


class TestDeployNetwork(TestCase):
    def setUp(self):
        self.inventory_hosts = [
            {'dst': '1.2.3.4'},
            {'dst': '2.3.4.5', 'port': 2222}
        ]
        self.log = self.set_up_patch('raptiformica.actions.deploy.log')
        self.read_inventory_file = self.set_up_patch('raptiformica.actions.deploy.read_inventory_file')
        self.read_inventory_file.return_value = self.inventory_hosts
        self.clean = self.set_up_patch('raptiformica.actions.deploy.clean')
        self.slave_machine = self.set_up_patch('raptiformica.actions.deploy.slave_machine')

    def test_deploy_network_logs_deploying_network_message(self):
        deploy_network('~/.raptiformica_inventory')

        self.assertTrue(self.log.info.called)

    def test_deploy_network_reads_inventory_file(self):
        deploy_network('~/.raptiformica_inventory')

        self.read_inventory_file.assert_called_once_with(
            '~/.raptiformica_inventory'
        )

    def test_deploy_network_raises_runtime_error_if_via(self):
        self.inventory_hosts = [
            {'dst': '1.2.3.4', 'via': '2.3.4.5'},
            {'dst': '2.3.4.5', 'port': 2222}
        ]
        self.read_inventory_file.return_value = self.inventory_hosts

        with self.assertRaises(RuntimeError):
            deploy_network('~/.raptiformica_inventory')

    def test_deploy_network_cleans_hosts(self):
        deploy_network('~/.raptiformica_inventory')

        expected_calls = [
            call('1.2.3.4', port=22),
            call('2.3.4.5', port=2222),
        ]
        self.assertCountEqual(expected_calls, self.clean.mock_calls)

    def test_deploy_network_slaves_hosts(self):
        deploy_network('~/.raptiformica_inventory')

        expected_calls = [
            call('1.2.3.4', port=22, server_type=None),
            call('2.3.4.5', port=2222, server_type=None),
        ]
        self.assertCountEqual(expected_calls, self.slave_machine.mock_calls)

    def test_deploy_network_slaves_hosts_as_specified_server_type(self):
        deploy_network('~/.raptiformica_inventory', server_type='workstation')

        expected_calls = [
            call('1.2.3.4', port=22, server_type='workstation'),
            call('2.3.4.5', port=2222, server_type='workstation'),
        ]
        self.assertCountEqual(expected_calls, self.slave_machine.mock_calls)
