from raptiformica.shell.raptiformica import advertise
from tests.testcase import TestCase


class TestAdvertise(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.raptiformica.log')
        self.run_raptiformica_command = self.set_up_patch(
            'raptiformica.shell.raptiformica.run_raptiformica_command'
        )

    def test_advertise_logs_advertise_message(self):
        advertise('1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_advertise_runs_raptiformica_command(self):
        advertise('1.2.3.4', port=2222)

        self.run_raptiformica_command.assert_called_once_with(
            'export PYTHONPATH=.; ./bin/raptiformica_advertise.py '
            '1.2.3.4 --port 2222', '1.2.3.4', port=2222
        )

    def test_advertise_returns_raptiformica_command_exit_code(self):
        ret = advertise('1.2.3.4', port=2222)

        self.assertEqual(ret, self.run_raptiformica_command.return_value)
