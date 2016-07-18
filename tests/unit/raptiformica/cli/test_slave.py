from mock import Mock

from raptiformica.cli import slave
from tests.testcase import TestCase


class TestSlave(TestCase):
    def setUp(self):
        self.parse_slave_arguments = self.set_up_patch('raptiformica.cli.parse_slave_arguments')
        self.parse_slave_arguments.return_value = Mock(
                host='1.2.3.4', port=22, server_type='headless', no_assimilate=False
        )
        self.slave_machine = self.set_up_patch('raptiformica.cli.slave_machine')

    def test_slave_parses_slave_arguments(self):
        slave()

        self.parse_slave_arguments.assert_called_once_with()

    def test_slave_slaves_machines(self):
        slave()

        self.slave_machine.assert_called_once_with(
            '1.2.3.4', port=22, assimilate=True, server_type='headless'
        )

    def test_slave_does_not_assimilate_machine_when_no_assimilate_is_passed(self):
        self.parse_slave_arguments.return_value = Mock(
                host='1.2.3.4', port=22, server_type='headless',
                no_assimilate=True
        )

        slave()

        self.slave_machine.assert_called_once_with(
            '1.2.3.4', port=22, assimilate=False, server_type='headless'
        )

