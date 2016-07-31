from raptiformica.actions.slave import deploy_meshnet
from tests.testcase import TestCase


class TestDeployMeshnet(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.slave.log')
        self.upload_self = self.set_up_patch('raptiformica.actions.slave.upload_self')
        self.mesh = self.set_up_patch('raptiformica.actions.slave.mesh')

    def test_deploy_meshnet_logs_deploying_meshnet_message(self):
        deploy_meshnet('1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_deploy_meshnet_uploads_self(self):
        deploy_meshnet('1.2.3.4', port=2222)

        self.upload_self.assert_called_once_with('1.2.3.4', port=2222)

    def test_deploy_meshnet_runs_raptiformica_mesh_command_on_remote_host(self):
        deploy_meshnet('1.2.3.4', port=2222)

        self.mesh.assert_called_once_with('1.2.3.4', port=2222)
