from mock import ANY

from raptiformica.actions.mesh import ensure_consul_agent
from tests.testcase import TestCase


class TestEnsureConsulAgent(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.flush_consul_agent_if_necessary = self.set_up_patch(
            'raptiformica.actions.mesh.flush_consul_agent_if_necessary'
        )
        self.check_if_consul_is_available = self.set_up_patch(
            'raptiformica.actions.mesh.check_if_consul_is_available'
        )
        self.restart_consul_agent_if_necessary = self.set_up_patch(
            'raptiformica.actions.mesh.restart_consul_agent_if_necessary'
        )
        self.reload_consul_agent_if_necessary = self.set_up_patch(
            'raptiformica.actions.mesh.reload_consul_agent_if_necessary'
        )
        self.restart_consul = self.set_up_patch(
            'raptiformica.actions.mesh.restart_consul'
        )
        self.block_until_consul_becomes_available = self.set_up_patch(
            'raptiformica.actions.mesh.block_until_consul_becomes_available'
        )

    def test_ensure_consul_agent_logs_ensuring_consul_agent_message(self):
        ensure_consul_agent()

        self.log.info.assert_called_once_with(ANY)

    def test_ensure_consul_agent_flushes_consul_agent_if_necessary(self):
        ensure_consul_agent()

        self.flush_consul_agent_if_necessary.assert_called_once_with()

    def test_ensure_consul_agent_checks_if_consul_is_available(self):
        ensure_consul_agent()

        self.check_if_consul_is_available.assert_called_once_with()

    def test_ensure_consul_agent_restarts_consul_agent_if_necessary_if_consul_already_available(self):
        self.check_if_consul_is_available.return_value = True

        ensure_consul_agent()

        self.restart_consul_agent_if_necessary.assert_called_once_with()

    def test_ensure_consul_agent_reloads_consul_agent_if_necessary_if_consul_already_available(self):
        self.check_if_consul_is_available.return_value = True

        ensure_consul_agent()

        self.reload_consul_agent_if_necessary.assert_called_once_with()

    def test_ensure_consul_agent_does_not_restart_consul_if_consul_available(self):
        self.check_if_consul_is_available.return_value = True

        ensure_consul_agent()

        self.assertFalse(self.restart_consul.called)

    def test_ensure_consul_agent_restarts_consul_if_not_available(self):
        self.check_if_consul_is_available.return_value = False

        ensure_consul_agent()

        self.restart_consul.assert_called_once_with()

    def test_ensure_consul_agent_does_not_restart_consul_agent_if_necessary_if_no_agent_available(self):
        self.check_if_consul_is_available.return_value = False

        ensure_consul_agent()

        self.assertFalse(self.restart_consul_agent_if_necessary.called)

    def test_ensure_consul_agent_does_not_reload_consul_agent_if_necessary_if_no_agent_available(self):
        self.check_if_consul_is_available.return_value = False

        ensure_consul_agent()

        self.assertFalse(self.reload_consul_agent_if_necessary.called)

    def test_ensure_consul_agent_blocks_until_consul_becomes_available(self):
        ensure_consul_agent()

        self.block_until_consul_becomes_available.assert_called_once_with()

    def test_ensure_consul_agent_is_retried_if_block_until_available_times_out(self):
        self.block_until_consul_becomes_available.side_effect = (TimeoutError, None)

        ensure_consul_agent()

        self.assertEqual(2, self.check_if_consul_is_available.call_count)
        self.assertEqual(2, self.restart_consul_agent_if_necessary.call_count)
        self.assertEqual(2, self.reload_consul_agent_if_necessary.call_count)
        self.assertEqual(2, self.block_until_consul_becomes_available.call_count)

    def test_ensure_consul_agent_is_only_retried_five_times(self):
        self.block_until_consul_becomes_available.side_effect = [
            TimeoutError
        ] * 5

        with self.assertRaises(TimeoutError):
            ensure_consul_agent()
