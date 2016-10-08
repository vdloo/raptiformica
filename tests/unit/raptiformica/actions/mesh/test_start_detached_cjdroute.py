from raptiformica.actions.mesh import start_detached_cjdroute, CJDROUTE_CONF_PATH
from tests.testcase import TestCase


class TestStartDetachedCjdroute(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.execute_process = self.set_up_patch(
                'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_start_detached_cjdroute_logs_starting_detached_cjdroute_message(self):
        start_detached_cjdroute()

        self.log.info.assert_called_once_with("Starting cjdroute in the background")

    def test_start_detached_cjdroute_starts_detached_cjdroute(self):
        start_detached_cjdroute()

        expected_command = "/usr/bin/env screen -d -m bash -c '" \
                           "cat {} | cjdroute --nobg" \
                           "'".format(CJDROUTE_CONF_PATH)
        self.execute_process.assert_called_once_with(
            expected_command,
            shell=True,
            buffered=False
        )

    def test_start_detached_cjdroute_raises_error_when_starting_detached_cjdroute_failed(self):
        process_output = (1, 'standard out output', 'standard error output')
        self.execute_process.return_value = process_output
        with self.assertRaises(RuntimeError):
            start_detached_cjdroute()
