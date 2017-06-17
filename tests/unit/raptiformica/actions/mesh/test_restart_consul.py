from raptiformica.actions.mesh import restart_consul
from tests.testcase import TestCase


class TestRestartConsul(TestCase):
    def setUp(self):
        self.clean_up_old_consul = self.set_up_patch(
            'raptiformica.actions.mesh.clean_up_old_consul'
        )
        self.start_detached_consul_agent = self.set_up_patch(
            'raptiformica.actions.mesh.start_detached_consul_agent'
        )
        self.write_consul_config_hash = self.set_up_patch(
            'raptiformica.actions.mesh.write_consul_config_hash'
        )

    def test_restart_consul_cleans_up_old_consul(self):
        restart_consul()

        self.clean_up_old_consul.assert_called_once_with()

    def test_restart_consul_starts_detached_consul_agent(self):
        restart_consul()

        self.start_detached_consul_agent.assert_called_once_with()

    def test_restart_consul_writes_consul_config_hash(self):
        restart_consul()

        self.write_consul_config_hash.assert_called_once_with()
