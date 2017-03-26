from mock import call

from raptiformica.actions.slave import provision_machine
from tests.testcase import TestCase


class TestProvision(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.slave.log')
        self.retrieve_provisioning_configs = self.set_up_patch(
            'raptiformica.actions.slave.retrieve_provisioning_configs'
        )
        self.retrieve_provisioning_configs.return_value = {
            'puppetfiles': {
                'source': 'https://github.com/vdloo/puppetfiles',
                'bootstrap': './papply.sh manifests/headless.pp'
            },
            'raptiformica-map': {
                'source': 'https://github.com/vdloo/raptiformica-map',
                'bootstrap': './deploy.sh'
            },
        }
        self.ensure_latest_source_from_artifacts = self.set_up_patch(
            'raptiformica.actions.slave.ensure_latest_source_from_artifacts'
        )
        self.run_resource_command = self.set_up_patch(
            'raptiformica.actions.slave.run_resource_command'
        )
        self.get_first_server_type = self.set_up_patch(
            'raptiformica.actions.slave.get_first_server_type'
        )
        self.get_first_server_type.return_value = 'headless'

    def test_provision_logs_provisioning_host_message(self):
        self.retrieve_provisioning_configs.return_value = {}

        provision_machine('1.2.3.4')

        self.log.info.assert_called_once_with(
            "Provisioning host 1.2.3.4 as server type {}".format(
                self.get_first_server_type.return_value
            )
        )

    def test_provision_retrieves_provisioning_config(self):
        provision_machine('1.2.3.4')

        self.retrieve_provisioning_configs.assert_called_once_with(
            self.get_first_server_type.return_value
        )

    def test_provision_retrieves_provisioning_config_for_specified_server_type(self):
        provision_machine('1.2.3.4', server_type='workstation')

        self.retrieve_provisioning_configs.assert_called_once_with('workstation')

    def test_provision_ensures_latest_source_for_all_provisioning_configs_on_the_remote_machine(self):
        provision_machine('1.2.3.4')

        expected_calls = (
            call(
                'https://github.com/vdloo/raptiformica-map',
                'raptiformica-map',
                host='1.2.3.4',
                port=22,
                only_cache=False
            ),
            call(
                'https://github.com/vdloo/puppetfiles',
                'puppetfiles',
                host='1.2.3.4',
                port=22,
                only_cache=False
            ),
        )
        self.assertCountEqual(
            self.ensure_latest_source_from_artifacts.mock_calls, expected_calls
        )

    def test_provision_runs_configured_bootstrap_command_for_all_provisioning_configs_on_the_remote_machine(self):
        provision_machine('1.2.3.4')

        expected_calls = (
            call(
                './papply.sh manifests/headless.pp',
                'puppetfiles',
                host='1.2.3.4',
                port=22
            ),
            call(
                './deploy.sh',
                'raptiformica-map',
                host='1.2.3.4',
                port=22
            )
        )
        self.assertCountEqual(
            self.run_resource_command.mock_calls,
            expected_calls
        )
