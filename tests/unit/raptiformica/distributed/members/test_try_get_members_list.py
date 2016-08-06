from raptiformica.distributed.members import try_get_members_list
from tests.testcase import TestCase


class TestTryGetMembersList(TestCase):
    def setUp(self):
        self.try_machine_command = self.set_up_patch('raptiformica.distributed.members.try_machine_command')
        self.host_and_port_pairs = [
            ('1.2.3.4', 2222),
            ('5.6.7.8', 22)
        ]

    def test_try_get_members_list_tries_machine_command(self):
        try_get_members_list(self.host_and_port_pairs)

        expected_command = ['consul', 'members']
        self.try_machine_command.assert_called_once_with(
            self.host_and_port_pairs,
            expected_command,
            attempt_message="Trying to get members list from {}:{}",
            all_failed_message="Could not list members in the distributed network. "
                               "Maybe no meshnet has been established yet. "
                               "Do you have at least three machines running?"
        )