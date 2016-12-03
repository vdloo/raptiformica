from mock import ANY

from raptiformica.actions.mesh import configure_meshing_services
from tests.testcase import TestCase


class TestConfigureMeshingServices(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.configure_cjdroute_conf = self.set_up_patch(
            'raptiformica.actions.mesh.configure_cjdroute_conf'
        )
        self.configure_consul_conf = self.set_up_patch(
            'raptiformica.actions.mesh.configure_consul_conf'
        )

    def test_configure_meshing_services_logs_starting_meshing_services_message(self):
        configure_meshing_services()

        self.log.info.assert_called_once_with(ANY)

    def test_configure_meshing_services_configures_cjdroute_conf(self):
        configure_meshing_services()

        self.configure_cjdroute_conf.assert_called_once_with()

    def test_configure_meshing_services_configures_consul_conf(self):
        configure_meshing_services()

        self.configure_consul_conf.assert_called_once_with()
