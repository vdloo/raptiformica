from raptiformica.actions.mesh import stop_detached_cjdroute
from tests.testcase import TestCase


class TestStopDetachedCjdroute(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_stop_detached_cjdroute_logs_stopping_detached_cjdroute_message(self):
        stop_detached_cjdroute()

        self.log.info.assert_called_once_with("Stopping cjdroute in the background")

    def test_stop_detached_cjdroute_stops_detached_cjdroute(self):
        stop_detached_cjdroute()

        expected_command = "pkill -f 'cjdroute --nobg'"
        self.execute_process.assert_called_once_with(
            expected_command,
            shell=True,
            buffered=False
        )

    def test_stop_detached_cjdroute_does_not_raise_error_when_stopping_returned_nonzero(self):
        process_output = (1, 'standard out output', 'standard error output')
        self.execute_process.return_value = process_output
        stop_detached_cjdroute()
