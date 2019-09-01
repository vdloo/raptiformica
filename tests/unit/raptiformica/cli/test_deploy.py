from mock import Mock, call

from raptiformica.cli import deploy
from tests.testcase import TestCase


class TestDeploy(TestCase):
    def setUp(self):
        self.parse_deploy_arguments = self.set_up_patch(
            'raptiformica.cli.parse_deploy_arguments'
        )
        self.parse_deploy_arguments.return_value = Mock(
            inventory='~/.raptiformica_inventory',
            server_type='headless',
            modules=[
                'vdloo/simulacra',
                'vdloo/raptiformica-map'
            ],
            concurrent=3,
            no_assimilate=False,
            no_after_assimilate=False,
            no_after_mesh=False,
            no_provision=False
        )
        self.load_module = self.set_up_patch(
            'raptiformica.cli.load_module'
        )
        self.deploy_network = self.set_up_patch(
            'raptiformica.cli.deploy_network'
        )

    def test_deploy_parses_deploy_arguments(self):
        deploy()

        self.parse_deploy_arguments.assert_called_once_with()

    def test_deploy_loads_modules_if_any(self):
        deploy()

        expected_calls = [
            call('vdloo/simulacra'),
            call('vdloo/raptiformica-map'),
        ]
        self.assertEqual(
            expected_calls, self.load_module.mock_calls
        )

    def test_deploy_does_not_load_modules_if_none(self):
        self.parse_deploy_arguments.return_value.modules = []

        deploy()

        self.assertFalse(self.load_module.called)

    def test_deploy_deploys_network(self):
        deploy()

        self.deploy_network.assert_called_once_with(
            '~/.raptiformica_inventory',
            server_type='headless',
            concurrent=3,
            assimilate=True,
            after_assimilate=True,
            after_mesh=True,
            provision=True
        )
