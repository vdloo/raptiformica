from raptiformica.actions.mesh import start_meshing_services
from tests.testcase import TestCase


class TestStartMeshingServices(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.start_detached_cjdroute = self.set_up_patch('raptiformica.actions.mesh.start_detached_cjdroute')
        self.start_detached_consul_agent = self.set_up_patch('raptiformica.actions.mesh.start_detached_consul_agent')

    def test_start_meshing_services_logs_meshing_services_message(self):
        start_meshing_services()

        self.log.info.assert_called_once_with("Starting meshing services")

    def test_start_meshing_services_starts_detached_cjdroute(self):
        start_meshing_services()

        self.start_detached_cjdroute.assert_called_once_with()

    def test_start_meshing_services_starts_detached_consul_agent(self):
        start_meshing_services()

        self.start_detached_consul_agent.assert_called_once_with()

