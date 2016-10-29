from raptiformica.actions.destroy import shutdown_all_instances, SHUTDOWN_SLEEP
from tests.testcase import TestCase


class TestShutdownAllInstances(TestCase):
    def setUp(self):
        self.host_and_port_pairs_from_config = self.set_up_patch(
            'raptiformica.actions.destroy.host_and_port_pairs_from_config'
        )
        self.try_issue_shutdown = self.set_up_patch(
            'raptiformica.actions.destroy.try_issue_shutdown'
        )
        self.try_issue_shutdown.return_value = False
        self.sleep = self.set_up_patch(
            'raptiformica.actions.destroy.sleep'
        )

    def test_shutdown_all_instances_gets_host_and_port_pairs_from_config(self):
        shutdown_all_instances()

        self.host_and_port_pairs_from_config.assert_called_once_with()

    def test_shutdown_all_instances_tries_issuing_shutdown(self):
        shutdown_all_instances()

        self.try_issue_shutdown.assert_called_once_with(
            self.host_and_port_pairs_from_config.return_value
        )

    def test_shutdown_all_instances_does_not_sleep_if_no_global_shutdown_successfully_issued(self):
        shutdown_all_instances()

        self.assertFalse(self.sleep.called)

    def test_shutdown_all_instances_sleeps_if_shutdown_successfully_issued(self):
        self.try_issue_shutdown.return_value = True

        shutdown_all_instances()

        self.sleep.assert_called_once_with(SHUTDOWN_SLEEP)
