from mock import ANY

from raptiformica.actions.mesh import ensure_no_consul_running
from tests.testcase import TestCase


class TestEnsureNoConsulRunning(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.run_command_print_ready = self.set_up_patch(
            'raptiformica.actions.mesh.run_command_print_ready'
        )

    def test_ensure_no_consul_running_logs_stopping_any_consul_agent_message(self):
        ensure_no_consul_running()

        self.log.info.assert_called_once_with(ANY)

    def test_ensure_no_consul_running_kills_any_running_consul_agents(self):
        ensure_no_consul_running()

        expected_command = "ps aux | grep [c]onsul | awk '{print $2}' | " \
                           "xargs --no-run-if-empty -I {} " \
                           "sh -c \"grep -q docker /proc/{}/cgroup && " \
                           "grep -qv docker /proc/1/cgroup || kill {}\""
        self.run_command_print_ready.assert_called_once_with(
            expected_command,
            shell=True,
            buffered=False
        )
        self.assertIn(
            'ps aux |', expected_command,
            'It should list all processes on the system'
        )
        self.assertIn(
            '| grep [c]onsul |', expected_command,
            'Should find the processes with consul in the name, '
            'excluding this one'
        )
        self.assertIn(
            "| awk '{print $2}' |", expected_command,
            'Should print the PID of the processes matching the name'
        )
        self.assertIn(
            "xargs --no-run-if-empty", expected_command,
            'Should map over the found PIDs, do nothing if no matches'
        )
        self.assertIn(
            "-I {} sh -c \"grep -q docker /proc/{}/cgroup && "
            "grep -qv docker /proc/1/cgroup || kill {}\"",
            expected_command,
            'Should only kill processes not in Docker containers unless '
            'running inside a Docker, those could have their own raptiformica '
            'instances running'
        )
