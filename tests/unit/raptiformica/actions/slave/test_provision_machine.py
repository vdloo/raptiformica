from raptiformica.actions.slave import provision_machine
from raptiformica.settings.types import get_first_server_type
from tests.testcase import TestCase


class TestProvision(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.slave.log')
        self.retrieve_provisioning_config = self.set_up_patch(
            'raptiformica.actions.slave.retrieve_provisioning_config'
        )
        self.retrieve_provisioning_config.return_value = (
            'https://github.com/vdloo/puppetfiles',
            'puppetfiles',
            './papply.sh manifests/headless.pp'
        )
        self.ensure_latest_source = self.set_up_patch(
            'raptiformica.actions.slave.ensure_latest_source'
        )
        self.run_configured_bootstrap_command = self.set_up_patch(
            'raptiformica.actions.slave.run_configured_bootstrap_command'
        )

    def test_provision_logs_provisioning_host_message(self):
        provision_machine('1.2.3.4')

        self.log.info.assert_called_once_with(
            "Provisioning host 1.2.3.4 as server type {}".format(get_first_server_type())
        )

    def test_provision_retrieves_provisioning_config(self):
        provision_machine('1.2.3.4')

        self.retrieve_provisioning_config.assert_called_once_with(
                get_first_server_type()
        )

    def test_provision_retrieves_provisioning_config_for_specified_server_type(self):
        provision_machine('1.2.3.4', server_type='workstation')

        self.retrieve_provisioning_config.assert_called_once_with('workstation')

    def test_provision_ensures_latest_source_on_the_remote_machine(self):
        provision_machine('1.2.3.4')

        self.ensure_latest_source.assert_called_once_with(
            'https://github.com/vdloo/puppetfiles',
            'puppetfiles',
            '1.2.3.4',
            port=22
        )

    def test_provision_runs_configured_bootstrap_command(self):
        provision_machine('1.2.3.4')

        self.run_configured_bootstrap_command.assert_called_once_with(
            './papply.sh manifests/headless.pp',
            'puppetfiles',
            '1.2.3.4',
            port=22
        )
