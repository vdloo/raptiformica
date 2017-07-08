from raptiformica.actions.prune import clean_up_stale_instance
from tests.testcase import TestCase


class TestCleanUpStaleInstance(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.prune.log')
        self.compute_checkout_directory = 'var/machines/docker/headless/a_generated_uuid'
        self.clean_up_stale_instance_command = "[ -f ubuntu64/container_id ] && " \
                                               "cat ubuntu64/container_id | " \
                                               "xargs sudo docker rm -f || /bin/true"
        self.args = (
            self.compute_checkout_directory,
            self.clean_up_stale_instance_command
        )
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )

        self.process_output = (0, 'standard out output', 'standard error output')
        self.execute_process.return_value = self.process_output

    def test_clean_up_stale_instance_logs_cleaning_up_stale_instance_message(self):
        clean_up_stale_instance(*self.args)

        self.assertTrue(self.log.info.called)

    def test_clean_up_stale_instance_runs_clean_up_stale_instance_command_on_local_host(self):
        clean_up_stale_instance(*self.args)

        expected_command = ['sh', '-c',
                            'cd var/machines/'
                            'docker/headless/a_generated_uuid; '
                            '{}'.format(self.clean_up_stale_instance_command)]
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=True,
            shell=False,
            timeout=1800
        )

    def test_clean_up_stale_instance_does_not_raise_error_when_command_failed(self):
        self.process_output = (1, '', 'standard error output')
        self.execute_process.return_value = self.process_output

        clean_up_stale_instance(*self.args)
