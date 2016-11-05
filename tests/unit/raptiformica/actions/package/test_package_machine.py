from raptiformica.actions.package import package_machine
from tests.testcase import TestCase


class TestPackageMachine(TestCase):
    def setUp(self):
        self.get_first_server_type = self.set_up_patch(
            'raptiformica.actions.package.get_first_server_type'
        )
        self.get_first_server_type.return_value = 'headless'
        self.get_first_compute_type = self.set_up_patch(
            'raptiformica.actions.package.get_first_compute_type'
        )
        self.get_first_compute_type.return_value = 'vagrant'
        self.retrieve_package_machine_config = self.set_up_patch(
            'raptiformica.actions.package.retrieve_package_machine_config'
        )
        self.run_command = self.set_up_patch(
            'raptiformica.actions.package.run_command'
        )

    def test_package_machine_gets_first_server_type_if_no_server_type_specified(self):
        package_machine()

        self.get_first_server_type.assert_called_once_with()

    def test_package_machine_does_not_get_first_server_type_if_server_type_specified(self):
        package_machine(server_type='headless')

        self.assertFalse(self.get_first_server_type.called)

    def test_package_machine_gets_first_compute_type_if_no_compute_type_specified(self):
        package_machine()

        self.get_first_compute_type.assert_called_once_with()

    def test_package_machine_does_not_get_first_compute_type_if_compute_type_specified(self):
        package_machine(compute_type='vagrant')

        self.assertFalse(self.get_first_compute_type.called)

    def test_package_machine_does_not_retrieve_package_machine_config_if_only_check_available(self):
        package_machine(only_check_available=True)

        self.assertFalse(self.retrieve_package_machine_config.called)

    def test_package_machine_does_not_run_package_command_if_only_check_available(self):
        package_machine(only_check_available=True)

        self.assertFalse(self.run_command.called)

    def test_package_machine_retrieves_package_machine_config(self):
        package_machine()

        self.retrieve_package_machine_config.assert_called_once_with(
            server_type=self.get_first_server_type.return_value,
            compute_type=self.get_first_compute_type.return_value
        )

    def test_package_machine_runs_package_command(self):
        package_machine()

        self.run_command.assert_called_once_with(
            self.retrieve_package_machine_config.return_value,
            buffered=False,
            shell=True
        )
