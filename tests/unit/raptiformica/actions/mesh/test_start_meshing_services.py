from raptiformica.actions.mesh import start_meshing_services
from tests.testcase import TestCase


class TestStartMeshingServices(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.start_detached_cjdroute = self.set_up_patch('raptiformica.actions.mesh.start_detached_cjdroute')
        self.ensure_ipv6_routing = self.set_up_patch('raptiformica.actions.mesh.ensure_ipv6_routing')
        self.start_detached_consul_agent = self.set_up_patch('raptiformica.actions.mesh.start_detached_consul_agent')
        self.sleep = self.set_up_patch('raptiformica.actions.mesh.sleep')

    def test_start_meshing_services_logs_meshing_services_message(self):
        start_meshing_services()

        self.log.info.assert_called_once_with("Starting meshing services")

    def test_start_meshing_services_starts_detached_cjdroute(self):
        start_meshing_services()

        self.start_detached_cjdroute.assert_called_once_with()

    def test_start_meshing_services_waits_a_bit_for_cjdroute_to_initialize(self):
        start_meshing_services()

        self.sleep.assert_called_once_with(10)

    def test_start_meshing_services_ensure_ipv6_routing(self):
        start_meshing_services()

        self.ensure_ipv6_routing.assert_called_once_with()

    def test_start_meshing_services_starts_detached_consul_agent(self):
        start_meshing_services()

        self.start_detached_consul_agent.assert_called_once_with()

