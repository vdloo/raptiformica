from raptiformica.actions.mesh import attempt_join_meshnet
from raptiformica.settings import MUTABLE_CONFIG
from tests.testcase import TestCase


class TestAttemptJoinMeshnet(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.load_config = self.set_up_patch('raptiformica.actions.mesh.load_config')
        self.configure_cjdroute_conf = self.set_up_patch('raptiformica.actions.mesh.configure_cjdroute_conf')
        self.configure_consul_conf = self.set_up_patch('raptiformica.actions.mesh.configure_consul_conf')
        self.start_meshing_services = self.set_up_patch('raptiformica.actions.mesh.start_meshing_services')
        self.enough_neighbours = self.set_up_patch('raptiformica.actions.mesh.enough_neighbours')
        self.join_meshnet = self.set_up_patch('raptiformica.actions.mesh.join_meshnet')

    def test_attempt_join_meshnet_logs_meshing_machine_message(self):
        attempt_join_meshnet()

        self.assertTrue(self.log.info.called)

    def test_attempt_join_meshnet_loads_mutable_config(self):
        attempt_join_meshnet()

        self.load_config.assert_called_once_with(MUTABLE_CONFIG)

    def test_attempt_join_meshnet_configures_cjdroute_config(self):
        attempt_join_meshnet()

        self.configure_cjdroute_conf.assert_called_once_with(
            self.load_config.return_value
        )

    def test_attempt_join_meshnet_configures_consul_config(self):
        attempt_join_meshnet()

        self.configure_consul_conf.assert_called_once_with(
            self.load_config.return_value
        )

    def test_attempt_join_meshnet_starts_meshing_services(self):
        attempt_join_meshnet()

        self.start_meshing_services.assert_called_once_with()

    def test_attempt_join_meshnet_checks_if_there_are_enough_neighbours(self):
        attempt_join_meshnet()

        self.enough_neighbours.assert_called_once_with(
            self.load_config.return_value
        )

    def test_attempt_join_meshnet_joins_meshnet_if_enough_neighbours(self):
        self.enough_neighbours.return_value = True

        attempt_join_meshnet()

        self.join_meshnet.assert_called_once_with(
            self.load_config.return_value
        )

    def test_attempt_join_meshnet_does_not_join_meshnet_if_not_enough_neighbours(self):
        self.enough_neighbours.return_value = False

        attempt_join_meshnet()

        self.assertFalse(self.join_meshnet.called)
