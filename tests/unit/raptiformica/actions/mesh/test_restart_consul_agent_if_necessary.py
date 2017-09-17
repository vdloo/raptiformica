from raptiformica.actions.mesh import restart_consul_agent_if_necessary, ConsulSharedSecretChanged
from tests.testcase import TestCase


class TestRestartConsulAgentIfNecessary(TestCase):
    def setUp(self):
        self.raise_if_shared_secret_changed = self.set_up_patch(
            'raptiformica.actions.mesh.raise_if_shared_secret_changed'
        )
        self.raise_if_shared_secret_changed.side_effect = ConsulSharedSecretChanged
        self.remove_old_consul_keyring = self.set_up_patch(
            'raptiformica.actions.mesh.remove_old_consul_keyring'
        )
        self.restart_consul = self.set_up_patch(
            'raptiformica.actions.mesh.restart_consul'
        )

    def test_restart_consul_agent_if_necessary_checks_if_consul_shared_secret_changed(self):
        restart_consul_agent_if_necessary()

        self.raise_if_shared_secret_changed.assert_called_once_with()

    def test_restart_consul_agent_if_necessary_removes_old_consul_keyring_if_shared_secret_changed(self):
        restart_consul_agent_if_necessary()

        self.remove_old_consul_keyring.assert_called_once_with()

    def test_restart_consul_agent_if_necessary_restarts_consul_if_shared_secret_changed(self):
        restart_consul_agent_if_necessary()

        self.restart_consul.assert_called_once_with()

    def test_restart_consul_agent_if_necessary_does_not_remove_old_consul_keyring_if_no_change(self):
        self.raise_if_shared_secret_changed.side_effect = None

        restart_consul_agent_if_necessary()

        self.assertFalse(self.remove_old_consul_keyring.called)

    def test_restart_consul_agent_if_necessary_does_not_restart_consul_if_no_change(self):
        self.raise_if_shared_secret_changed.side_effect = None

        restart_consul_agent_if_necessary()

        self.assertFalse(self.restart_consul.called)
