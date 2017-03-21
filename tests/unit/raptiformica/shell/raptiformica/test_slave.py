from raptiformica.shell.raptiformica import slave
from tests.testcase import TestCase


class TestSlave(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.raptiformica.log')
        self.get_first_server_type = self.set_up_patch(
            'raptiformica.shell.raptiformica.get_first_server_type'
        )
        self.get_first_server_type.return_value = 'headless'
        self.run_raptiformica_command = self.set_up_patch(
            'raptiformica.shell.raptiformica.run_raptiformica_command'
        )

    def test_slave_logs_slave_message(self):
        slave('1.2.3.3', 2223, '1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_slave_gets_first_server_type(self):
        slave('1.2.3.3', 2223, '1.2.3.4', port=2222)

        self.get_first_server_type.assert_called_once_with()

    def test_slave_does_not_get_first_server_type_if_server_type_provided(self):
        slave('1.2.3.3', 2223, '1.2.3.4', port=2222, server_type='workstation')

        self.assertFalse(self.get_first_server_type.called)

    def test_slave_runs_raptiformica_command(self):
        slave('1.2.3.3', 2223, '1.2.3.4', port=2222)

        self.run_raptiformica_command.assert_called_once_with(
            'export PYTHONPATH=.; ./bin/raptiformica_slave.py '
            '--verbose 1.2.3.3 --port 2223 --server-type headless',
            '1.2.3.4', port=2222
        )

    def test_slave_runs_raptiformica_command_with_specified_server_type(self):
        slave('1.2.3.3', 2223, '1.2.3.4', port=2222, server_type='workstation')

        self.run_raptiformica_command.assert_called_once_with(
            'export PYTHONPATH=.; ./bin/raptiformica_slave.py '
            '--verbose 1.2.3.3 --port 2223 --server-type workstation',
            '1.2.3.4', port=2222
        )

    def test_slave_returns_raptiformica_command_exit_code(self):
        ret = slave('1.2.3.3', 2223, '1.2.3.4', port=2222)

        self.assertEqual(ret, self.run_raptiformica_command.return_value)
