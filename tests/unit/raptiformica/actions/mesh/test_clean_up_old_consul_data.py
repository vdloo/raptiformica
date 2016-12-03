from mock import ANY

from raptiformica.actions.mesh import clean_up_old_consul_data
from tests.testcase import TestCase


class TestCleanUpOldConsulData(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.rmtree = self.set_up_patch('raptiformica.actions.mesh.rmtree')

    def test_clean_up_old_consul_data_logs_cleaning_up_message(self):
        clean_up_old_consul_data()

        self.log.info.assert_called_once_with(ANY)

    def test_clean_up_old_consul_data_ensures_consul_data_dir_is_removed(self):
        clean_up_old_consul_data()

        self.rmtree.assert_called_once_with(
            '/opt/consul', ignore_errors=True
        )
