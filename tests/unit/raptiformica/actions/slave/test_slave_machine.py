from raptiformica.actions.slave import slave_machine
from raptiformica.settings.server import get_first_server_type
from tests.testcase import TestCase


class TestSlaveMachine(TestCase):
    def setUp(self):
        self.upload_self = self.set_up_patch('raptiformica.actions.slave.upload_self')
        self.provision = self.set_up_patch('raptiformica.actions.slave.provision')

    def test_slave_machine_uploads_raptiformica_to_the_remote_host(self):
        slave_machine('1.2.3.4')

        self.upload_self.assert_called_once_with('1.2.3.4', port=22)

    def test_slave_machine_uploads_raptiformica_to_the_remote_host_using_a_specified_port(self):
        slave_machine('1.2.3.4', port=2222, server_type='headless')

        self.upload_self.assert_called_once_with('1.2.3.4', port=2222)

    def test_slave_machine_provisions_host(self):
        slave_machine('1.2.3.4')

        self.provision.assert_called_once_with('1.2.3.4', port=22, server_type=get_first_server_type())

    def test_slave_machine_provisions_host_with_specified_server_type(self):
        slave_machine('1.2.3.4', port=2222, server_type='headless')

        self.provision.assert_called_once_with('1.2.3.4', port=2222, server_type='headless')
