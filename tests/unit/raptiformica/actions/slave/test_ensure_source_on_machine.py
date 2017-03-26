from unittest.mock import Mock

from mock import ANY, call

from raptiformica.actions.slave import ensure_source_on_machine
from tests.testcase import TestCase


class TestEnsureSourceOnMachine(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.actions.slave.log'
        )
        self.get_first_server_type = self.set_up_patch(
            'raptiformica.actions.slave.get_first_server_type'
        )
        self.retrieve_provisioning_configs = self.set_up_patch(
            'raptiformica.actions.slave.retrieve_provisioning_configs'
        )
        self.retrieve_provisioning_configs.return_value = {
            'puppetfiles': {'source': 'file:///some/repo/to/the/puppetfiles.git'},
            'vagrantfiles': {'source': 'https://example.com/some/repo/to/the/vagrantfiles.git'}
        }
        self.ensure_latest_source_from_artifacts = self.set_up_patch(
            'raptiformica.actions.slave.ensure_latest_source_from_artifacts'
        )

    def test_ensure_source_on_machine_logs_info(self):
        ensure_source_on_machine()

        self.log.info.assert_called_once_with(ANY)

    def test_ensure_source_on_machine_gets_first_server_type_if_none_is_provided(self):
        ensure_source_on_machine()

        self.get_first_server_type.assert_called_once_with()

    def test_ensure_source_on_machine_does_not_get_server_type_if_one_is_provided(self):
        ensure_source_on_machine(server_type='workstation')

        self.assertFalse(self.get_first_server_type.called)

    def test_ensure_source_on_machine_retrieves_provisioning_configs_of_specified_server_type(self):
        ensure_source_on_machine(server_type='workstation')

        self.retrieve_provisioning_configs.assert_called_once_with(
            'workstation'
        )

    def test_ensure_source_on_machine_retrieves_provisioning_configs_of_first_server_type_if_none_provided(self):
        ensure_source_on_machine()

        self.retrieve_provisioning_configs.assert_called_once_with(
            self.get_first_server_type.return_value
        )

    def test_ensure_source_on_machine_ensures_latest_source_from_artifacts_for_all_provisioning_configs(self):
        ensure_source_on_machine()

        expected_calls = (
            call(
                'file:///some/repo/to/the/puppetfiles.git',
                'puppetfiles', host=None, port=22,
                only_cache=False
            ),
            call(
                'https://example.com/some/repo/to/the/vagrantfiles.git',
                'vagrantfiles', host=None, port=22,
                only_cache=False
            )
        )
        self.assertCountEqual(
            self.ensure_latest_source_from_artifacts.mock_calls, expected_calls
        )

    def test_ensure_source_on_machine_ensures_latest_source_for_all_provisioning_configs_with_only_cache(self):
        ensure_source_on_machine(only_cache=True)

        expected_calls = (
            call(
                'file:///some/repo/to/the/puppetfiles.git',
                'puppetfiles', host=None, port=22,
                only_cache=True
            ),
            call(
                'https://example.com/some/repo/to/the/vagrantfiles.git',
                'vagrantfiles', host=None, port=22,
                only_cache=True
            )
        )
        self.assertCountEqual(
            self.ensure_latest_source_from_artifacts.mock_calls, expected_calls
        )

    def test_ensure_source_on_machine_ensures_latest_source_for_all_provisioning_configs_for_specified_host(self):
        ensure_source_on_machine(host='1.2.3.4')

        expected_calls = (
            call(
                'file:///some/repo/to/the/puppetfiles.git',
                'puppetfiles', host='1.2.3.4', port=22,
                only_cache=False
            ),
            call(
                'https://example.com/some/repo/to/the/vagrantfiles.git',
                'vagrantfiles', host='1.2.3.4', port=22,
                only_cache=False
            )
        )
        self.assertCountEqual(
            self.ensure_latest_source_from_artifacts.mock_calls, expected_calls
        )

    def test_ensure_source_on_machine_ensures_latest_source_for_all_provisioning_configs_for_specified_port(self):
        ensure_source_on_machine(host='1.2.3.4', port=4321)

        expected_calls = (
            call(
                'file:///some/repo/to/the/puppetfiles.git',
                'puppetfiles', host='1.2.3.4', port=4321,
                only_cache=False
            ),
            call(
                'https://example.com/some/repo/to/the/vagrantfiles.git',
                'vagrantfiles', host='1.2.3.4', port=4321,
                only_cache=False
            )
        )
        self.assertCountEqual(
            self.ensure_latest_source_from_artifacts.mock_calls, expected_calls
        )

    def test_ensure_source_on_machine_performs_callback_for_all_provisioning_configs(self):
        self.callback = Mock()

        ensure_source_on_machine(callback=self.callback)

        expected_calls = (
            call(
                'puppetfiles',
                {'source': 'file:///some/repo/to/the/puppetfiles.git'}
            ),
            call(
                'vagrantfiles',
                {'source': 'https://example.com/some/repo/to/the/vagrantfiles.git'}
            )
        )
        self.assertCountEqual(self.callback.mock_calls, expected_calls)
