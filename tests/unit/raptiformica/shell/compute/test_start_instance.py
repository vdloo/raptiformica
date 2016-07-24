from mock import call

from raptiformica.shell.compute import start_instance
from tests.testcase import TestCase


class TestStartInstance(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.compute.log')
        self.args = (
            'vagrant',
            "https://github.com/vdloo/vagrantfiles",
            "cd headless && vagrant up --provider=virtualbox",
            "cd headless && vagrant ssh-config | grep HostName | awk '{print$NF}'",
            "cd headless && vagrant ssh-config | grep Port | awk '{print$NF}'"
        )
        self.create_new_compute_type_directory = self.set_up_patch(
            'raptiformica.shell.compute.create_new_compute_type_directory'
        )
        self.boot_instance = self.set_up_patch('raptiformica.shell.compute.boot_instance')
        self.compute_attribute_get = self.set_up_patch('raptiformica.shell.compute.compute_attribute_get')

    def test_start_instance_logs_starting_new_instance_message(self):
        start_instance(*self.args)

        self.assertTrue(self.log.info.called)

    def test_start_instance_creates_new_compute_type_directory(self):
        start_instance(*self.args)

        self.create_new_compute_type_directory.assert_called_once_with(
            'vagrant', "https://github.com/vdloo/vagrantfiles"
        )

    def test_start_instance_boots_new_instance(self):
        start_instance(*self.args)

        self.boot_instance.assert_called_once_with(
            self.create_new_compute_type_directory.return_value,
            "cd headless && vagrant up --provider=virtualbox"
        )

    def test_start_instance_gets_host_and_port_of_new_instance(self):
        start_instance(*self.args)

        expected_calls = [
            call(
                self.create_new_compute_type_directory.return_value,
                "cd headless && vagrant ssh-config | grep HostName | awk '{print$NF}'",
                "hostname"
            ),
            call(
                self.create_new_compute_type_directory.return_value,
                "cd headless && vagrant ssh-config | grep Port | awk '{print$NF}'",
                "port"
            )
        ]
        self.assertCountEqual(expected_calls, self.compute_attribute_get.mock_calls)

    def test_start_instance_return_host_and_port(self):
        self.compute_attribute_get.side_effect = ['127.0.0.1', '2222']

        host, port = start_instance(*self.args)

        self.assertEqual(host, '127.0.0.1')
        self.assertEqual(port, '2222')
