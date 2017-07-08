from raptiformica.shell.ssh import verify_ssh_agent_running
from tests.testcase import TestCase


class TestVerifySSHAgentRunning(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.ssh.log')
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_verify_ssh_agent_running_logs_verifying_ssh_agent_running_message(self):
        verify_ssh_agent_running()

        self.assertTrue(self.log.info.called)

    def test_verify_ssh_agent_running_checks_the_ssh_agent_status(self):
        verify_ssh_agent_running()

        expected_command = ['ssh-add', '-l']
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=True,
            shell=False,
            timeout=1800
        )

    def test_verify_ssh_agent_running_raises_error_if_exit_code_is_nonzero(self):
        self.process_output = (1, 'The agent has no identities', '')
        self.execute_process.return_value = self.process_output

        with self.assertRaises(RuntimeError):
            verify_ssh_agent_running()

        self.process_output = (2, 'Could not open a connection to your authentication agent', '')
        self.execute_process.return_value = self.process_output

        with self.assertRaises(RuntimeError):
            verify_ssh_agent_running()

    def test_verify_ssh_agent_running_returns_exit_code(self):
        ret = verify_ssh_agent_running()

        self.assertEqual(ret, 0)
