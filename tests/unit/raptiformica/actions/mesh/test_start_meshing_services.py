from raptiformica.actions.mesh import start_meshing_services
from tests.testcase import TestCase


class TestStartMeshingServices(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.ensure_cjdns_routing = self.set_up_patch(
            'raptiformica.actions.mesh.ensure_cjdns_routing'
        )
        self.ensure_consul_agent = self.set_up_patch(
            'raptiformica.actions.mesh.ensure_consul_agent'
        )
        self.ensure_raptiformica_agent = self.set_up_patch(
            'raptiformica.actions.mesh.ensure_raptiformica_agent'
        )

    def test_start_meshing_services_ensures_raptiformica_agent(self):
        start_meshing_services()

        self.ensure_raptiformica_agent.assert_called_once_with()

    def test_start_meshing_services_logs_meshing_services_message(self):
        start_meshing_services()

        self.log.info.assert_called_once_with("Starting meshing services")

    def test_start_meshing_services_ensures_cjdns_routing(self):
        start_meshing_services()

        self.ensure_cjdns_routing.assert_called_once_with()

    def test_start_meshing_services_ensures_consul_agent(self):
        start_meshing_services()

        self.ensure_consul_agent.assert_called_once_with()
