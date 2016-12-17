from raptiformica.shell.raptiformica import inject
from tests.testcase import TestCase


class TestInject(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.raptiformica.log')
        self.run_raptiformica_command = self.set_up_patch(
            'raptiformica.shell.raptiformica.run_raptiformica_command'
        )

    def test_inject_logs_inject_message(self):
        inject('1.2.3.3', 2223, '1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_inject_runs_raptiformica_command(self):
        inject('1.2.3.3', 2223, '1.2.3.4', port=2222)

        self.run_raptiformica_command.assert_called_once_with(
            'export PYTHONPATH=.; ./bin/raptiformica_inject.py '
            '--verbose 1.2.3.3 --port 2223',
            '1.2.3.4', port=2222
        )

    def test_inject_returns_raptiformica_command_exit_code(self):
        ret = inject('1.2.3.3', 2223, '1.2.3.4', port=2222)

        self.assertEqual(ret, self.run_raptiformica_command.return_value)
