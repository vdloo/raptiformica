from unittest.mock import ANY

from raptiformica.settings.meshnet import bootstrap_host_to_neighbour
from tests.testcase import TestCase


class TestBootstrapHostToNeighbour(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.settings.meshnet.log')
        self.inject = self.set_up_patch('raptiformica.settings.meshnet.inject')

    def test_bootstrap_host_to_neighbour_logs_injecting_new_host_message(self):
        bootstrap_host_to_neighbour('1.2.3.4', 2222, '1.2.3.3', 22)

        self.log.info.assert_called_once_with(ANY)

    def test_bootstrap_host_to_neighbour_injects_host_and_port_into_neighbour_meshnet_config(self):
        bootstrap_host_to_neighbour('1.2.3.4', 2222, '1.2.3.3', 22)

        self.inject.assert_called_once_with(
            '1.2.3.4', 2222, '1.2.3.3', 22
        )
