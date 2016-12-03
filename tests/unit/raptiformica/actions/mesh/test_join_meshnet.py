from raptiformica.actions.mesh import join_meshnet
from tests.testcase import TestCase


class TestJoinMeshnet(TestCase):
    def setUp(self):
        self.get_config_mapping = self.set_up_patch(
            'raptiformica.actions.mesh.get_config_mapping'
        )
        self.join_consul_neighbours = self.set_up_patch(
            'raptiformica.actions.mesh.join_consul_neighbours'
        )

    def test_join_meshnet_gets_config_mapping(self):
        join_meshnet()

        self.get_config_mapping.assert_called_once_with()

    def test_join_meshnet_joins_consul_neighbours_from_config(self):
        join_meshnet()

        self.join_consul_neighbours.assert_called_once_with(
            self.get_config_mapping.return_value
        )
