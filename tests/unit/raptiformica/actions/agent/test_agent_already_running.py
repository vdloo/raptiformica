from raptiformica.actions.agent import agent_already_running
from tests.testcase import TestCase


class TestAgentAlreadyRunning(TestCase):
    def setUp(self):
        self.check_nonzero_exit = self.set_up_patch(
            'raptiformica.actions.agent.check_nonzero_exit'
        )
        self.check_nonzero_exit.return_value = True
        self._get_program_name = self.set_up_patch(
            'raptiformica.actions.agent._get_program_name'
        )
        self._get_program_name.return_value = 'raptiformica.actions.spawn'

    def test_agent_already_running_checks_if_there_is_another_agent_already_running(self):
        agent_already_running()

        expected_command = "ps aux | grep 'bin/[r]aptiformica_agent.py' | " \
                           "grep -v screen -i | grep python3 | grep -v 'sh -c' | " \
                           "awk '{print $2}' | xargs --no-run-if-empty -I {} " \
                           "sh -c \"grep -q docker /proc/{}/cgroup 2> /dev/null " \
                           "&& ! grep -q name=systemd:/docker /proc/1/cgroup || echo {}\" | " \
                           "wc -l | { read li; test $li -gt 0; }"
        self.check_nonzero_exit.assert_called_once_with(
            expected_command
        )

    def test_agent_already_running_allows_2_agents_to_run_if_check_runs_inside_agent(self):
        self._get_program_name.return_value = 'raptiformica.actions.agent'

        agent_already_running()

        expected_command = "ps aux | grep 'bin/[r]aptiformica_agent.py' | " \
                           "grep -v screen -i | grep python3 | grep -v 'sh -c' | " \
                           "awk '{print $2}' | xargs --no-run-if-empty -I {} " \
                           "sh -c \"grep -q docker /proc/{}/cgroup 2> /dev/null " \
                           "&& ! grep -q name=systemd:/docker /proc/1/cgroup || echo {}\" | " \
                           "wc -l | { read li; test $li -gt 1; }"
        self.check_nonzero_exit.assert_called_once_with(
            expected_command
        )

    def tests_agent_already_running_returns_true_if_check_exits_zero(self):
        ret = agent_already_running()

        self.assertTrue(ret)

    def tests_agent_already_running_returns_false_if_check_exits_nonzero(self):
        self.check_nonzero_exit.return_value = False

        ret = agent_already_running()

        self.assertFalse(ret)
