from mock import Mock

from raptiformica.cli import slave
from tests.testcase import TestCase


class TestSlave(TestCase):
    def setUp(self):
        self.parse_slave_arguments = self.set_up_patch(
            'raptiformica.cli.parse_slave_arguments'
        )
        self.parse_slave_arguments.return_value = Mock(
            no_provision=False, no_assimilate=False,
            host='1.2.3.4', port=22, server_type='headless'
        )
        # patching the original function instead of the function in the scope
        # of cli.py because this is a conditional import and so that function
        # won't be available to patch until the function that imports it is
        # evaluated.
        self.slave_machine = self.set_up_patch(
            'raptiformica.actions.slave.slave_machine'
        )

    def test_slave_parses_slave_arguments(self):
        slave()

        self.parse_slave_arguments.assert_called_once_with()

    def test_slave_slaves_machines(self):
        slave()

        self.slave_machine.assert_called_once_with(
            '1.2.3.4', port=22, provision=True,
            assimilate=True, server_type='headless',
        )

    def test_slave_does_not_assimilate_machine_when_no_assimilate_is_passed(self):
        self.parse_slave_arguments.return_value = Mock(
                host='1.2.3.4', port=22, server_type='headless',
                no_assimilate=True, no_provision=False
        )

        slave()

        self.slave_machine.assert_called_once_with(
            '1.2.3.4', port=22, provision=True,
            assimilate=False, server_type='headless'
        )

    def test_slave_does_not_provision_machine_when_no_provision_is_passed(self):
        self.parse_slave_arguments.return_value = Mock(
            host='1.2.3.4', port=22, server_type='headless',
            no_assimilate=False, no_provision=True
        )

        slave()

        self.slave_machine.assert_called_once_with(
            '1.2.3.4', port=22, provision=False,
            assimilate=True, server_type='headless'
        )
