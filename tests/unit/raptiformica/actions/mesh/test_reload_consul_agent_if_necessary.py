from raptiformica.actions.mesh import reload_consul_agent_if_necessary
from tests.testcase import TestCase


class TestReloadConsulAgentIfNecessary(TestCase):
    def setUp(self):
        self.consul_config_hash_outdated = self.set_up_patch(
            'raptiformica.actions.mesh.consul_config_hash_outdated'
        )
        self.clean_up_old_consul = self.set_up_patch(
            'raptiformica.actions.mesh.clean_up_old_consul'
        )
        self.reload_consul_agent = self.set_up_patch(
            'raptiformica.actions.mesh.reload_consul_agent'
        )
        self.write_consul_config_hash = self.set_up_patch(
            'raptiformica.actions.mesh.write_consul_config_hash'
        )

    def test_reload_consul_agent_if_necessary_checks_if_consul_config_hash_is_outdated(self):
        reload_consul_agent_if_necessary()

        self.consul_config_hash_outdated.assert_called_once_with()

    def test_reload_consul_agent_does_not_clean_up_old_consul_if_config_hash_still_up_to_date(self):
        self.consul_config_hash_outdated.return_value = False

        reload_consul_agent_if_necessary()

        self.assertFalse(self.clean_up_old_consul.called)

    def test_reload_consul_agent_does_not_reload_consul_agent_if_config_hash_still_up_to_date(self):
        self.consul_config_hash_outdated.return_value = False

        reload_consul_agent_if_necessary()

        self.assertFalse(self.reload_consul_agent.called)

    def test_reload_consul_agent_does_not_write_consul_config_hash_if_hash_still_up_to_date(self):
        self.consul_config_hash_outdated.return_value = False

        reload_consul_agent_if_necessary()

        self.assertFalse(self.reload_consul_agent.called)

    def test_reload_consul_agent_reloads_consul_agent_if_config_hash_is_outdated(self):
        self.consul_config_hash_outdated.return_value = True

        reload_consul_agent_if_necessary()

        self.reload_consul_agent.assert_called_once_with()

    def test_reload_consul_agent_writes_consul_config_hash_if_config_hash_is_outdated(self):
        self.consul_config_hash_outdated.return_value = True

        reload_consul_agent_if_necessary()

        self.write_consul_config_hash.assert_called_once_with()
