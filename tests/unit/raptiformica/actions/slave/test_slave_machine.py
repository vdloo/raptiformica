from raptiformica.actions.slave import slave_machine
from raptiformica.settings.types import get_first_server_type
from tests.testcase import TestCase


class TestSlaveMachine(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.slave.log')
        self.upload_self = self.set_up_patch('raptiformica.actions.slave.upload_self')
        self.provision_machine = self.set_up_patch('raptiformica.actions.slave.provision_machine')
        self.assimilate_machine = self.set_up_patch('raptiformica.actions.slave.assimilate_machine')
        self.deploy_meshnet = self.set_up_patch('raptiformica.actions.slave.deploy_meshnet')

    def test_slave_machine_logs_slaving_machine_message(self):
        slave_machine('1.2.3.4')

        self.assertTrue(self.log.info.called)

    def test_slave_machine_uploads_raptiformica_to_the_remote_host(self):
        slave_machine('1.2.3.4')

        self.upload_self.assert_called_once_with('1.2.3.4', port=22)

    def test_slave_machine_uploads_raptiformica_to_the_remote_host_using_a_specified_port(self):
        slave_machine('1.2.3.4', port=2222, server_type='headless')

        self.upload_self.assert_called_once_with('1.2.3.4', port=2222)

    def test_slave_machine_provisions_host_if_provision(self):
        slave_machine('1.2.3.4')

        self.provision_machine.assert_called_once_with(
            '1.2.3.4', port=22, server_type=get_first_server_type()
        )

    def test_slave_machine_does_not_provision_host_if_provision_is_false(self):
        slave_machine('1.2.3.4', provision=False)

        self.assertFalse(self.provision_machine.called)

    def test_slave_machine_provisions_host_with_specified_server_type(self):
        slave_machine('1.2.3.4', port=2222, server_type='headless')

        self.provision_machine.assert_called_once_with(
            '1.2.3.4', port=2222, server_type='headless'
        )

    def test_slave_machine_assimilates_machine_if_assimilate(self):
        slave_machine('1.2.3.4', port=2222, assimilate=True)

        self.assimilate_machine.assert_called_once_with(
            '1.2.3.4', port=2222, uuid=None
        )

    def test_slave_machine_assimilates_machines_if_assimilate_with_optional_uuid(self):
        slave_machine('1.2.3.4', port=2222, assimilate=True, uuid='some_uuid_1234')

        self.assimilate_machine.assert_called_once_with(
            '1.2.3.4', port=2222, uuid='some_uuid_1234'
        )

    def test_slave_machine_does_not_assimilate_if_assimilate_is_false(self):
        slave_machine('1.2.3.4', port=2222, assimilate=False)

        self.assertFalse(self.assimilate_machine.called)

    def test_slave_machine_deploys_meshnet_if_assimilate(self):
        slave_machine('1.2.3.4', port=2222, assimilate=True)

        self.deploy_meshnet.assert_called_once_with('1.2.3.4', port=2222)

    def test_slave_machine_does_not_deploy_meshnet_if_assimilate_is_false(self):
        slave_machine('1.2.3.4', port=2222, assimilate=False)

        self.assertFalse(self.deploy_meshnet.called)
