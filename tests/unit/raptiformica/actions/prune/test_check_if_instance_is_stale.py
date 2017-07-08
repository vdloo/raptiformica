from raptiformica.actions.prune import check_if_instance_is_stale
from tests.testcase import TestCase


class TestCheckIfInstanceIsStale(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.prune.log')
        self.compute_checkout_directory = 'var/machines/docker/headless/a_generated_uuid'
        self.detect_stale_instance_command = "[ -f ubuntu64/container_id ] && " \
                                             "sudo docker ps --no-trunc | " \
                                             "grep -f ubuntu64/container_id"
        self.args = (
            self.compute_checkout_directory,
            self.detect_stale_instance_command
        )
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )

        self.process_output = (0, 'standard out output', 'standard error output')
        self.execute_process.return_value = self.process_output

    def test_check_if_instance_is_stale_logs_detecting_stale_instance_message(self):
        check_if_instance_is_stale(*self.args)

        self.assertEqual(self.log.debug.call_count, 2)

    def test_check_if_instance_is_stale_runs_detect_stale_instance_command_on_local_host(self):
        check_if_instance_is_stale(*self.args)

        expected_command = ['sh', '-c',
                            'cd var/machines/'
                            'docker/headless/a_generated_uuid; '
                            '{}'.format(self.detect_stale_instance_command)]
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=True,
            shell=False,
            timeout=1800
        )

    def test_check_if_instance_is_stale_returns_true_if_instance_is_stale(self):
        self.process_output = (1, '', 'standard error output')

        self.execute_process.return_value = self.process_output

        ret = check_if_instance_is_stale(*self.args)

        self.assertTrue(ret)

    def test_check_if_instance_is_stale_does_not_log_instance_still_active_debug_message_if_not_still_active(self):
        self.process_output = (1, '', 'standard error output')
        self.execute_process.return_value = self.process_output

        check_if_instance_is_stale(*self.args)

        self.assertEqual(self.log.debug.call_count, 1)

    def test_check_if_instance_is_stale_returns_false_if_instance_is_still_active(self):
        self.execute_process.return_value = self.process_output

        ret = check_if_instance_is_stale(*self.args)

        self.assertFalse(ret)
