from raptiformica.actions.mesh import attempt_join_meshnet
from tests.testcase import TestCase


class TestAttemptJoinMeshnet(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.configure_meshing_services = self.set_up_patch(
            'raptiformica.actions.mesh.configure_meshing_services'
        )
        self.start_meshing_services = self.set_up_patch(
            'raptiformica.actions.mesh.start_meshing_services'
        )
        self.enough_neighbours = self.set_up_patch('raptiformica.actions.mesh.enough_neighbours')
        self.join_meshnet = self.set_up_patch('raptiformica.actions.mesh.join_meshnet')

    def test_attempt_join_meshnet_logs_meshing_machine_message(self):
        attempt_join_meshnet()

        self.assertTrue(self.log.info.called)

    def test_attempt_join_meshnet_configures_meshing_services(self):
        attempt_join_meshnet()

        self.configure_meshing_services.assert_called_once_with()

    def test_attempt_join_meshnet_starts_meshing_services(self):
        attempt_join_meshnet()

        self.start_meshing_services.assert_called_once_with()

    def test_attempt_join_meshnet_checks_if_there_are_enough_neighbours(self):
        attempt_join_meshnet()

        self.enough_neighbours.assert_called_once_with()

    def test_attempt_join_meshnet_joins_meshnet_if_enough_neighbours(self):
        self.enough_neighbours.return_value = True

        attempt_join_meshnet()

        self.join_meshnet.assert_called_once_with()

    def test_attempt_join_meshnet_does_not_join_meshnet_if_not_enough_neighbours(self):
        self.enough_neighbours.return_value = False

        attempt_join_meshnet()

        self.assertFalse(self.join_meshnet.called)
