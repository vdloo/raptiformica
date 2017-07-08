from functools import partial

from mock import call
from tests.testcase import TestCase

from raptiformica.distributed.exec import try_machine_command


class TestTryMachineCommand(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.distributed.exec.log')
        self.host_and_port_pairs = [
            ('1.2.3.4', '2222'),
            ('5.6.7.8', '22'),
            ('9.9.9.9', '1222'),
            ('9.9.9.8', '1223')
        ]
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (1, 'standard out output', 'standard error output')
        self.execute_process.return_value = self.process_output
        self.command = ['/bin/true']

    def test_try_machine_command_logs_debug_message_for_every_attempted_host(self):
        try_machine_command(self.host_and_port_pairs, self.command)

        expected_calls = map(call, [
            "trying command on 1.2.3.4:2222",
            "trying command on 5.6.7.8:22",
            "trying command on 9.9.9.9:1222",
            "Ran out of hosts to try!",
        ])
        self.assertCountEqual(self.log.debug.mock_calls, expected_calls)

    def test_try_machine_command_runs_remote_command_on_three_hosts_until_one_returns_zero(self):
        self.execute_process.side_effect = [
            self.process_output,
            self.process_output,
            (0, 'standard out output', 'standard error output')
        ]

        try_machine_command(self.host_and_port_pairs, self.command)

        expected_command_as_list1 = ['/usr/bin/env', 'ssh', '-A',
                                     '-o', 'ConnectTimeout=5',
                                     '-o', 'StrictHostKeyChecking=no',
                                     '-o', 'UserKnownHostsFile=/dev/null',
                                     '-o', 'PasswordAuthentication=no',
                                     'root@1.2.3.4',
                                     '-p', '2222', '/bin/true']
        expected_command_as_list2 = ['/usr/bin/env', 'ssh', '-A',
                                     '-o', 'ConnectTimeout=5',
                                     '-o', 'StrictHostKeyChecking=no',
                                     '-o', 'UserKnownHostsFile=/dev/null',
                                     '-o', 'PasswordAuthentication=no',
                                     'root@5.6.7.8',
                                     '-p', '22', '/bin/true']
        expected_command_as_list3 = ['/usr/bin/env', 'ssh', '-A',
                                     '-o', 'ConnectTimeout=5',
                                     '-o', 'StrictHostKeyChecking=no',
                                     '-o', 'UserKnownHostsFile=/dev/null',
                                     '-o', 'PasswordAuthentication=no',
                                     'root@9.9.9.9',
                                     '-p', '1222', '/bin/true']
        expected_command_list = [
            expected_command_as_list1,
            expected_command_as_list2,
            expected_command_as_list3
        ]
        expected_calls = map(
            partial(
                call,
                buffered=True,
                shell=False,
                timeout=1800
            ),
            expected_command_list
        )
        self.assertCountEqual(self.execute_process.mock_calls, expected_calls)

    def test_try_machine_command_runs_remote_command_on_the_amount_of_specified_hosts_until_one_returns_zero(self):
        self.execute_process.side_effect = [
            self.process_output,
            (0, 'standard out output', 'standard error output')
        ]

        try_machine_command(self.host_and_port_pairs, self.command, attempt_limit=2)

        expected_command_as_list1 = ['/usr/bin/env', 'ssh', '-A',
                                     '-o', 'ConnectTimeout=5',
                                     '-o', 'StrictHostKeyChecking=no',
                                     '-o', 'UserKnownHostsFile=/dev/null',
                                     '-o', 'PasswordAuthentication=no',
                                     'root@1.2.3.4',
                                     '-p', '2222', '/bin/true']
        expected_command_as_list2 = ['/usr/bin/env', 'ssh', '-A',
                                     '-o', 'ConnectTimeout=5',
                                     '-o', 'StrictHostKeyChecking=no',
                                     '-o', 'UserKnownHostsFile=/dev/null',
                                     '-o', 'PasswordAuthentication=no',
                                     'root@5.6.7.8',
                                     '-p', '22', '/bin/true']
        expected_command_list = [
            expected_command_as_list1,
            expected_command_as_list2,
        ]
        expected_calls = map(
            partial(
                call,
                buffered=True,
                shell=False,
                timeout=1800
            ),
            expected_command_list
        )
        self.assertCountEqual(self.execute_process.mock_calls, expected_calls)

    def test_try_machine_command_returns_remote_command_output(self):
        self.execute_process.side_effect = [
            self.process_output,
            self.process_output,
            (0, 'standard out output\n', 'standard error output')
        ]

        ret = try_machine_command(self.host_and_port_pairs, self.command)

        self.assertEqual(ret, ('standard out output', '9.9.9.9', '1222'))

    def test_try_machine_command_returns_tuple_of_nones_if_no_remote_host_succeeded_running_the_command(self):
        ret = try_machine_command(self.host_and_port_pairs, self.command)

        self.assertEqual(ret, (None, None, None))
