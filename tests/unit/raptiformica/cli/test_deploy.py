from mock import Mock

from raptiformica.cli import deploy
from tests.testcase import TestCase


class TestDeploy(TestCase):
    def setUp(self):
        self.parse_deploy_arguments = self.set_up_patch(
            'raptiformica.cli.parse_deploy_arguments'
        )
        self.parse_deploy_arguments.return_value = Mock(
            inventory='~/.raptiformica_inventory',
            server_type='headless'
        )
        self.deploy_network = self.set_up_patch(
            'raptiformica.cli.deploy_network'
        )

    def test_deploy_parses_deploy_arguments(self):
        deploy()

        self.parse_deploy_arguments.assert_called_once_with()

    def test_deploy_deploys_network(self):
        deploy()

        self.deploy_network.assert_called_once_with(
            '~/.raptiformica_inventory', server_type='headless'
        )
