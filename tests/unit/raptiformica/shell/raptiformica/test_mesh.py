from raptiformica.shell.raptiformica import mesh
from tests.testcase import TestCase


class TestMesh(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.raptiformica.log')
        self.run_raptiformica_command = self.set_up_patch(
            'raptiformica.shell.raptiformica.run_raptiformica_command'
        )

    def test_mesh_logs_joining_mesh_message(self):
        mesh('1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_mesh_runs_raptiformica_command(self):
        mesh('1.2.3.4', port=2222)

        self.run_raptiformica_command.assert_called_once_with(
            'export PYTHONPATH=.; ./bin/raptiformica_mesh.py --verbose',
            '1.2.3.4', port=2222
        )

    def tst_mesh_returns_raptiformica_command_exit_code(self):
        ret = mesh('1.2.3.4', port=2222)

        self.assertEqual(ret, self.run_raptiformica_command.return_value)
