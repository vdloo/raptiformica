from raptiformica.actions.mesh import mesh_machine
from tests.testcase import TestCase


class TestMeshMachine(TestCase):
    def setUp(self):
        self.attempt_join_meshnet = self.set_up_patch(
            'raptiformica.actions.mesh.attempt_join_meshnet'
        )
        self.fire_hooks = self.set_up_patch(
            'raptiformica.actions.mesh.fire_hooks'
        )

    def test_mesh_machine_attempts_join_network(self):
        mesh_machine()

        self.attempt_join_meshnet.assert_called_once_with()

    def test_mesh_machine_fires_after_mesh_hooks(self):
        mesh_machine()

        self.fire_hooks.assert_called_once_with(
            'after_mesh'
        )

    def test_mesh_machine_does_not_fire_after_mesh_hook_if_no_after_mesh(self):
        mesh_machine(after_mesh=False)

        self.assertFalse(self.fire_hooks.called)
