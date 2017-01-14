from raptiformica.cli import mesh
from tests.testcase import TestCase


class TestMesh(TestCase):
    def setUp(self):
        self.parse_mesh_arguments = self.set_up_patch(
            'raptiformica.cli.parse_mesh_arguments'
        )
        # patching the original function instead of the function in the scope
        # of cli.py because this is a conditional import and so that function
        # won't be available to patch until the function that imports it is
        # evaluated.
        self.mesh_machine = self.set_up_patch(
            'raptiformica.actions.mesh.mesh_machine'
        )

    def test_mesh_parses_mesh_arguments(self):
        mesh()

        self.parse_mesh_arguments.assert_called_once_with()

    def test_mesh_meshes_machine(self):
        mesh()

        self.mesh_machine.assert_called_once_with()
