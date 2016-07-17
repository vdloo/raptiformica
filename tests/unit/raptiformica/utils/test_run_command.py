from subprocess import PIPE

from raptiformica.utils import run_command
from tests.testcase import TestCase


class TestRunCommand(TestCase):
    def setUp(self):
        self.command_as_list = ['/bin/ls', '/root']
        self.p_open = self.set_up_patch('raptiformica.utils.Popen')
        self.standard_out = 'standard out output'
        self.standard_err = 'standard error output'
        self.p_open.return_value.communicate.return_value = (self.standard_out, self.standard_err)

    def test_run_command_instantiates_process_object(self):
        run_command(self.command_as_list)

        self.p_open.assert_called_once_with(self.command_as_list, stdout=PIPE, stderr=PIPE)

    def test_run_command_communicates_for_output(self):
        run_command(self.command_as_list)

        self.p_open.return_value.communicate.assert_called_once_with()

    def test_run_command_returns_exit_code_and_standard_out_and_standard_err(self):
        ret = run_command(self.command_as_list)

        expected_output = (
            self.p_open.return_value.returncode,
            self.standard_out,
            self.standard_err
        )
        self.assertEqual(ret, expected_output)
