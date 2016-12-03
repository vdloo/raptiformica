from mock import ANY

from raptiformica.actions.mesh import clean_up_old_consul
from tests.testcase import TestCase


class TestCleanUpOldConsul(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.ensure_no_consul_running = self.set_up_patch(
            'raptiformica.actions.mesh.ensure_no_consul_running'
        )
        self.clean_up_old_consul_data = self.set_up_patch(
            'raptiformica.actions.mesh.clean_up_old_consul_data'
        )

    def test_clean_up_old_consul_logs_cleaning_up_old_processes_and_data_message(self):
        clean_up_old_consul()

        self.log.info.assert_called_once_with(ANY)

    def test_clean_up_old_consul_ensures_no_consul_running(self):
        clean_up_old_consul()

        self.ensure_no_consul_running.assert_called_once_with()

    def test_clean_up_old_consul_cleans_up_old_consul_data(self):
        clean_up_old_consul()

        self.clean_up_old_consul_data.assert_called_once_with()
