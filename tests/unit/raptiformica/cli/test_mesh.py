from raptiformica.cli import mesh
from tests.testcase import TestCase


class TestMesh(TestCase):
    def setUp(self):
        self.parse_mesh_arguments = self.set_up_patch(
            'raptiformica.cli.parse_mesh_arguments'
        )
        self.mesh_machine = self.set_up_patch(
            'raptiformica.cli.mesh_machine'
        )

    def test_mesh_parses_mesh_arguments(self):
        mesh()

        self.parse_mesh_arguments.assert_called_once_with()

    def test_mesh_meshes_machine(self):
        mesh()

        self.mesh_machine.assert_called_once_with()
