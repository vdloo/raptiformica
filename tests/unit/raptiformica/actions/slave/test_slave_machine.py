from raptiformica.actions.slave import slave_machine
from tests.testcase import TestCase


class TestSlaveMachine(TestCase):
    def setUp(self):
        self.upload_self = self.set_up_patch('raptiformica.actions.slave.upload_self')

    def test_slave_machine_uploads_raptiformica_to_the_remote_host(self):
        slave_machine('1.2.3.4')

        self.upload_self.assert_called_once_with('1.2.3.4', port=22)

    def test_slave_machine_uploads_raptiformica_to_the_remote_host_using_a_specified_port(self):
        slave_machine('1.2.3.4', port=2222)

        self.upload_self.assert_called_once_with('1.2.3.4', port=2222)
