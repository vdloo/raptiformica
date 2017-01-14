from subprocess import PIPE

from raptiformica.settings import CACHE_DIR
from raptiformica.shell.execute import execute_process
from tests.testcase import TestCase


class TestExecuteProcess(TestCase):
    def setUp(self):
        self.command_as_list = ['/bin/ls', '/root']
        self.p_open = self.set_up_patch('raptiformica.shell.execute.Popen')
        self.standard_out = 'standard out output'
        self.standard_err = 'standard error output'
        self.p_open.return_value.communicate.return_value = (
            self.standard_out, self.standard_err
        )
        self.environ = {
            'some': 'env_var',
            'RAPTIFORMICA_CACHE_DIR': CACHE_DIR
        }
        self.set_up_patch('raptiformica.shell.execute.environ', self.environ)

    def test_execute_process_instantiates_process_object(self):
        execute_process(self.command_as_list)

        self.p_open.assert_called_once_with(
            self.command_as_list, stdout=PIPE, stderr=PIPE,
            bufsize=-1, shell=False,
            universal_newlines=True,
            env=self.environ
        )

    def test_execute_process_passes_overwritten_cache_dir_from_settings_to_env(self):
        self.set_up_patch('raptiformica.shell.execute.CACHE_DIR', '.raptiformica.d.test')

        execute_process(self.command_as_list)

        self.environ['RAPTIFORMICA_CACHE_DIR'] = '.raptiformica.d.test'
        self.p_open.assert_called_once_with(
            self.command_as_list, stdout=PIPE, stderr=PIPE,
            bufsize=-1, shell=False,
            universal_newlines=True,
            env=self.environ
        )

    def test_execute_process_instantiates_process_object_as_shell_if_shell(self):
        execute_process(self.command_as_list, shell=True)

        self.p_open.assert_called_once_with(
            self.command_as_list, stdout=PIPE, stderr=PIPE,
            bufsize=-1, shell=True,
            universal_newlines=True,
            env=self.environ
        )

    def test_execute_process_communicates_for_output(self):
        execute_process(self.command_as_list)

        self.p_open.return_value.communicate.assert_called_once_with()

    def test_execute_process_returns_exit_code_and_standard_out_and_standard_err(self):
        ret = execute_process(self.command_as_list)

        expected_output = (
            self.p_open.return_value.returncode,
            self.standard_out,
            self.standard_err
        )
        self.assertEqual(ret, expected_output)
