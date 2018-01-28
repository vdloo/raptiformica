from raptiformica.actions.mesh import flush_consul_agent_if_necessary
from tests.testcase import TestCase


class TestFlushConsulAgentIfNecessary(TestCase):
    def setUp(self):
        self.consul_outage_detected = self.set_up_patch(
            'raptiformica.actions.mesh.consul_outage_detected'
        )
        self.consul_outage_detected.return_value = False
        self.remove_consul_local_state = self.set_up_patch(
            'raptiformica.actions.mesh.remove_consul_local_state'
        )

    def test_flush_consul_agent_if_necessary_checks_if_consul_outage_detected(self):
        flush_consul_agent_if_necessary()

        self.consul_outage_detected.assert_called_once_with()

    def test_flush_consul_agent_if_necessary_removes_consul_local_state_if_detected(self):
        self.consul_outage_detected.return_value = True

        flush_consul_agent_if_necessary()

        self.remove_consul_local_state.assert_called_once_with()

    def test_flush_consul_agent_if_necessary_does_not_remove_consul_local_state_if_not_detected(self):
        flush_consul_agent_if_necessary()

        self.assertFalse(self.remove_consul_local_state.called)
