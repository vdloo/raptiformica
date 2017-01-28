from mock import ANY

from raptiformica.actions.mesh import ensure_consul_agent
from tests.testcase import TestCase


class TestEnsureConsulAgent(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.check_if_consul_is_available = self.set_up_patch(
            'raptiformica.actions.mesh.check_if_consul_is_available'
        )
        self.reload_consul_agent_if_necessary = self.set_up_patch(
            'raptiformica.actions.mesh.reload_consul_agent_if_necessary'
        )
        self.clean_up_old_consul = self.set_up_patch(
            'raptiformica.actions.mesh.clean_up_old_consul'
        )
        self.block_until_consul_port_is_free = self.set_up_patch(
            'raptiformica.actions.mesh.block_until_consul_port_is_free'
        )
        self.start_detached_consul_agent = self.set_up_patch(
            'raptiformica.actions.mesh.start_detached_consul_agent'
        )
        self.write_consul_config_hash = self.set_up_patch(
            'raptiformica.actions.mesh.write_consul_config_hash'
        )
        self.block_until_consul_becomes_available = self.set_up_patch(
            'raptiformica.actions.mesh.block_until_consul_becomes_available'
        )

    def test_ensure_consul_agent_logs_ensuring_consul_agent_message(self):
        ensure_consul_agent()

        self.log.info.assert_called_once_with(ANY)

    def test_ensure_consul_agent_checks_if_consul_is_available(self):
        ensure_consul_agent()

        self.check_if_consul_is_available.assert_called_once_with()

    def test_ensure_consul_agent_reloads_consul_agent_if_consul_already_available(self):
        self.check_if_consul_is_available.return_value = True

        ensure_consul_agent()

        self.reload_consul_agent_if_necessary.assert_called_once_with()

    def test_ensure_consul_agent_does_not_clean_up_old_consul_if_consul_available(self):
        self.check_if_consul_is_available.return_value = True

        ensure_consul_agent()

        self.assertFalse(self.clean_up_old_consul.called)

    def test_ensure_consul_agent_does_not_block_until_consul_port_is_free_if_consul_available(self):
        self.check_if_consul_is_available.return_value = True

        ensure_consul_agent()

        self.assertFalse(self.block_until_consul_port_is_free.called)

    def test_ensure_consul_agent_does_not_start_a_new_detached_consul_agent_if_consul_already_available(self):
        self.check_if_consul_is_available.return_value = True

        ensure_consul_agent()

        self.assertFalse(self.start_detached_consul_agent.called)

    def test_ensure_consul_agent_does_not_write_consul_config_hash_if_consul_already_available(self):
        self.check_if_consul_is_available.return_value = True

        ensure_consul_agent()

        # it might still write a new consul config hash as part of a reload
        # if it turns out that the current running consul agent is using an
        # outdated config.
        self.assertFalse(self.write_consul_config_hash.called)

    def test_ensure_consul_agent_cleans_up_any_old_consul_agents_if_not_available(self):
        self.check_if_consul_is_available.return_value = False

        ensure_consul_agent()

        self.clean_up_old_consul.assert_called_once_with()

    def test_ensure_consul_agent_blocks_until_consul_port_is_free_if_not_available(self):
        self.check_if_consul_is_available.return_value = False

        ensure_consul_agent()

        self.block_until_consul_port_is_free.assert_called_once_with()

    def test_ensure_consul_agent_starts_detached_consul_agent_if_consul_agent_not_available(self):
        self.check_if_consul_is_available.return_value = False

        ensure_consul_agent()

        self.start_detached_consul_agent.assert_called_once_with()

    def test_ensure_consul_agent_writes_consul_config_hash_if_consul_agent_not_available(self):
        self.check_if_consul_is_available.return_value = False

        ensure_consul_agent()

        self.write_consul_config_hash.assert_called_once_with()

    def test_ensure_consul_agent_does_not_reload_consul_agent_if_necessary_if_no_agent_available(self):
        self.check_if_consul_is_available.return_value = False

        ensure_consul_agent()

        self.assertFalse(self.reload_consul_agent_if_necessary.called)

    def test_ensure_consul_agent_blocks_until_consul_becomes_available(self):
        ensure_consul_agent()

        self.block_until_consul_becomes_available.assert_called_once_with()
