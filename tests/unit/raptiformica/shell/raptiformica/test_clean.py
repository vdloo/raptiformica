from raptiformica.shell.raptiformica import clean
from tests.testcase import TestCase


class TestClean(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.raptiformica.log')
        self.run_raptiformica_command = self.set_up_patch(
            'raptiformica.shell.raptiformica.run_raptiformica_command'
        )

    def test_clean_logs_clean_message(self):
        clean('1.2.3.3', 2223)

        self.assertTrue(self.log.info.called)

    def test_clean_runs_raptiformica_command(self):
        clean('1.2.3.3', 2223)

        self.run_raptiformica_command.assert_called_once_with(
            'export PYTHONPATH=.; ./bin/raptiformica_clean.py '
            '--verbose',
            '1.2.3.3', port=2223
        )

    def test_clean_returns_raptiformica_command_exit_code(self):
        ret = clean('1.2.3.3', 2223)

        self.assertEqual(ret, self.run_raptiformica_command.return_value)
