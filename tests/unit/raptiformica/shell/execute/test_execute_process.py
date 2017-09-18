from subprocess import PIPE

from raptiformica.settings import conf
from raptiformica.shell.execute import execute_process, COMMAND_TIMEOUT
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
            'RAPTIFORMICA_CACHE_DIR': conf().CACHE_DIR
        }
        self.set_up_patch('raptiformica.shell.execute.environ', self.environ)
        self.terminate_on_timeout = self.set_up_patch(
            'raptiformica.shell.execute.terminate_on_timeout'
        )
        self.terminate_on_timeout.return_value.__enter__ = lambda a: None
        self.terminate_on_timeout.return_value.__exit__ = lambda a, b, c, d: None
        self.write_real_time_output = self.set_up_patch(
            'raptiformica.shell.execute.write_real_time_output'
        )

    def test_execute_process_instantiates_process_object(self):
        execute_process(self.command_as_list)

        self.p_open.assert_called_once_with(
            self.command_as_list, stdout=PIPE, stderr=PIPE,
            bufsize=-1, shell=False,
            universal_newlines=True,
            env=self.environ
        )

    def test_execute_process_passes_overwritten_cache_dir_from_settings_to_env(self):
        configuration = self.set_up_patch('raptiformica.shell.execute.conf')
        configuration.return_value.CACHE_DIR = '.raptiformica.d.test'

        execute_process(self.command_as_list)

        self.environ['RAPTIFORMICA_CACHE_DIR'] = '.raptiformica.d.test'
        self.p_open.assert_called_once_with(
            self.command_as_list, stdout=PIPE, stderr=PIPE,
            bufsize=-1, shell=False,
            universal_newlines=True,
            env=self.environ
        )

    def test_execute_process_instantiates_process_object_as_shell_if_shell(self):
        execute_process(' '.join(self.command_as_list), shell=True)

        self.p_open.assert_called_once_with(
            ' '.join(self.command_as_list),
            stdout=PIPE, stderr=PIPE,
            bufsize=-1, shell=True,
            universal_newlines=True,
            env=self.environ
        )

    def test_execute_process_terminates_on_timeout(self):
        execute_process(self.command_as_list)

        self.terminate_on_timeout.assert_called_once_with(
            self.p_open.return_value, COMMAND_TIMEOUT, self.command_as_list
        )

    def test_execute_process_terminates_on_specified_timeout(self):
        execute_process(self.command_as_list, timeout=10)

        self.terminate_on_timeout.assert_called_once_with(
            self.p_open.return_value, 10, self.command_as_list
        )

    def test_execute_process_does_not_write_real_time_output(self):
        execute_process(self.command_as_list)

        self.assertFalse(self.write_real_time_output.called)

    def test_execute_process_writes_real_time_output_if_not_buffered(self):
        execute_process(self.command_as_list, buffered=False)

        self.write_real_time_output.assert_called_once_with(
            self.p_open.return_value
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
