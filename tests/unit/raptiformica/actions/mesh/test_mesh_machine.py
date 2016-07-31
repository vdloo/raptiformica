from raptiformica.actions.mesh import mesh_machine
from raptiformica.settings import MUTABLE_CONFIG
from tests.testcase import TestCase


class TestMeshMachine(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.load_config = self.set_up_patch('raptiformica.actions.mesh.load_config')
        self.configure_cjdroute_conf = self.set_up_patch('raptiformica.actions.mesh.configure_cjdroute_conf')
        self.configure_consul_conf = self.set_up_patch('raptiformica.actions.mesh.configure_consul_conf')
        self.start_meshing_services = self.set_up_patch('raptiformica.actions.mesh.start_meshing_services')
        self.enough_neighbours = self.set_up_patch('raptiformica.actions.mesh.enough_neighbours')
        self.join_meshnet = self.set_up_patch('raptiformica.actions.mesh.join_meshnet')

    def test_mesh_machine_logs_meshing_machine_message(self):
        mesh_machine()

        self.assertTrue(self.log.info.called)

    def test_mesh_machine_loads_mutable_config(self):
        mesh_machine()

        self.load_config.assert_called_once_with(MUTABLE_CONFIG)

    def test_mesh_machine_configures_cjdroute_config(self):
        mesh_machine()

        self.configure_cjdroute_conf.assert_called_once_with(
            self.load_config.return_value
        )

    def test_mesh_machine_configures_consul_config(self):
        mesh_machine()

        self.configure_consul_conf.assert_called_once_with(
            self.load_config.return_value
        )

    def test_mesh_machine_starts_meshing_services(self):
        mesh_machine()

        self.start_meshing_services.assert_called_once_with()

    def test_mesh_machine_checks_if_there_are_enough_neighbours(self):
        mesh_machine()

        self.enough_neighbours.assert_called_once_with(
            self.load_config.return_value
        )

    def test_mesh_machine_joins_meshnet_if_enough_neighbours(self):
        self.enough_neighbours.return_value = True

        mesh_machine()

        self.join_meshnet.assert_called_once_with(
            self.load_config.return_value
        )

    def test_mesh_machine_does_not_join_meshnet_if_not_enough_neighbours(self):
        self.enough_neighbours.return_value = False

        mesh_machine()

        self.assertFalse(self.join_meshnet.called)
