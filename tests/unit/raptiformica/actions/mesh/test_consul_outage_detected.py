from raptiformica.actions.mesh import consul_outage_detected, WAIT_FOR_CONSUL_TIMEOUT
from tests.testcase import TestCase


class TestConsulOutageDetected(TestCase):
    def setUp(self):
        self.run_command = self.set_up_patch(
            'raptiformica.actions.mesh.run_command'
        )
        self.run_command.return_value = (0, 'output', '')

    def test_consul_outage_detected_runs_kv_get_for_api_version(self):
        consul_outage_detected()

        expected_command = ['consul', 'kv', 'get', '/raptiformica/raptiformica_api_version']

        self.run_command.assert_called_once_with(expected_command, timeout=WAIT_FOR_CONSUL_TIMEOUT)

    def test_consul_outage_detected_returns_false_if_no_outage_detected(self):
        ret = consul_outage_detected()

        self.assertFalse(ret)

    def test_consul_outage_detected_returns_false_if_no_stderr_retrieved(self):
        self.run_command.return_value = (1, 'output', None)

        ret = consul_outage_detected()

        self.assertFalse(ret)

    def test_consul_outage_detected_returns_true_if_got_500_from_consul_agent(self):
        self.run_command.return_value = (1, '', 'Error querying Consul agent: Unexpected response code: 500\n')

        ret = consul_outage_detected()

        self.assertTrue(ret)
