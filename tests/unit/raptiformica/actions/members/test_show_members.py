from raptiformica.actions.members import show_members
from tests.testcase import TestCase


class TestShowMembers(TestCase):
    def setUp(self):
        self.host_and_port_pairs_from_mutable_config = self.set_up_patch(
            'raptiformica.actions.members.host_and_port_pairs_from_mutable_config'
        )
        self.try_get_members_list = self.set_up_patch('raptiformica.actions.members.try_get_members_list')
        self.try_get_members_list.return_value = 'Node                                     ' \
                                                 'Address                                         ' \
                                                 'Status  ' \
                                                 'Type    ' \
                                                 'Build  ' \
                                                 'Protocol  ' \
                                                 'DC'
        self.print = self.set_up_patch('raptiformica.actions.members.print')

    def test_show_members_gets_host_and_port_pairs_from_mutable_config(self):
        show_members()

        self.host_and_port_pairs_from_mutable_config()

    def test_show_members_tries_to_get_members_list_from_host_and_port_pairs(self):
        show_members()

        self.try_get_members_list.assert_called_once_with(
            self.host_and_port_pairs_from_mutable_config.return_value
        )

    def test_show_members_prints_members_list_when_it_could_be_retrieved(self):
        show_members()

        self.print.assert_called_once_with(
            self.try_get_members_list.return_value
        )

    def test_show_members_prints_nothing_when_no_members_list_could_be_retrieved(self):
        self.try_get_members_list.return_value = None

        show_members()

        self.assertFalse(self.print.called)
