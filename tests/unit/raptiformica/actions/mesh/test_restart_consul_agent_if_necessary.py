from raptiformica.actions.mesh import restart_consul_agent_if_necessary
from tests.testcase import TestCase


class TestRestartConsulAgentIfNecessary(TestCase):
    def setUp(self):
        self.consul_shared_secret_changed = self.set_up_patch(
            'raptiformica.actions.mesh.consul_shared_secret_changed'
        )
        self.consul_shared_secret_changed.return_value = True
        self.remove_old_consul_keyring = self.set_up_patch(
            'raptiformica.actions.mesh.remove_old_consul_keyring'
        )
        self.restart_consul = self.set_up_patch(
            'raptiformica.actions.mesh.restart_consul'
        )

    def test_restart_consul_agent_if_necessary_checks_if_consul_shared_secret_changed(self):
        restart_consul_agent_if_necessary()

        self.consul_shared_secret_changed.assert_called_once_with()

    def test_restart_consul_agent_if_necessary_removes_old_consul_keyring_if_shared_secret_changed(self):
        restart_consul_agent_if_necessary()

        self.remove_old_consul_keyring.assert_called_once_with()

    def test_restart_consul_agent_if_necessary_restarts_consul_if_shared_secret_changed(self):
        restart_consul_agent_if_necessary()

        self.restart_consul.assert_called_once_with()

    def test_restart_consul_agent_if_necessary_does_not_remove_old_consul_keyring_if_no_change(self):
        self.consul_shared_secret_changed.return_value = False

        restart_consul_agent_if_necessary()

        self.assertFalse(self.remove_old_consul_keyring.called)

    def test_restart_consul_agent_if_necessary_does_not_restart_consul_if_no_change(self):
        self.consul_shared_secret_changed.return_value = False

        restart_consul_agent_if_necessary()

        self.assertFalse(self.restart_consul.called)
