from raptiformica.actions.spawn import start_compute_type
from tests.testcase import TestCase


class TestStartComputeType(TestCase):
    def setUp(self):
        self.retrieve_start_instance_config = self.set_up_patch(
            'raptiformica.actions.spawn.retrieve_start_instance_config'
        )
        self.retrieve_start_instance_config.return_value = (
            'https://github.com/vdloo/vagrantfiles',
            'cd headless && vagrant up --provider=virtualbox',
            "cd headless && vagrant ssh-config | grep HostName | awk '{print$NF}'",
            "cd headless && vagrant ssh-config | grep Port | awk '{print$NF}'"
        )
        self.start_instance = self.set_up_patch(
            'raptiformica.actions.spawn.start_instance'
        )
        self.get_first_server_type = self.set_up_patch(
                'raptiformica.actions.spawn.get_first_server_type'
        )
        self.get_first_server_type.return_value = 'headless'
        self.get_first_compute_type = self.set_up_patch(
                'raptiformica.actions.spawn.get_first_compute_type'
        )
        self.get_first_server_type.return_value = 'docker'

    def test_start_compute_type_retrieves_start_instance_config_for_default_types(self):
        start_compute_type()

        self.retrieve_start_instance_config.assert_called_once_with(
            server_type=self.get_first_server_type.return_value,
            compute_type=self.get_first_compute_type.return_value
        )

    def test_start_compute_type_starts_instance_of_the_default_compute_type(self):
        start_compute_type()

        self.start_instance.assert_called_once_with(
            self.get_first_server_type.return_value,
            self.get_first_compute_type.return_value,
            *self.retrieve_start_instance_config.return_value
        )

    def test_start_compute_type_retrieves_start_instance_config_for_specified_types(self):
        start_compute_type(server_type='htpc', compute_type='docker')

        self.retrieve_start_instance_config.assert_called_once_with(
            server_type='htpc',
            compute_type='docker',
        )

    def test_start_compute_type_starts_instance_for_specified_compute_type(self):
        start_compute_type(server_type='htpc', compute_type='docker')

        self.start_instance.assert_called_once_with(
            'htpc',
            'docker',
            *self.retrieve_start_instance_config.return_value
        )

    def test_start_compute_type_returns_connection_information(self):
        ret = start_compute_type(server_type='htpc', compute_type='docker')

        self.assertEqual(ret, self.start_instance.return_value)
