from raptiformica.cli import members
from tests.testcase import TestCase


class TestMembers(TestCase):
    def setUp(self):
        self.parse_members_arguments = self.set_up_patch(
            'raptiformica.cli.parse_members_arguments'
        )
        self.parse_members_arguments.return_value.rejoin = False
        self.attempt_join_meshnet = self.set_up_patch(
            'raptiformica.cli.attempt_join_meshnet'
        )
        self.show_members = self.set_up_patch(
            'raptiformica.cli.show_members'
        )

    def test_members_parses_members_arguments(self):
        members()

        self.parse_members_arguments.assert_called_once_with()

    def test_members_shows_members(self):
        members()

        self.show_members.assert_called_once_with()
        self.assertFalse(self.attempt_join_meshnet.called)

    def test_members_rejoins_members_if_specified(self):
        self.parse_members_arguments.return_value.rejoin = True

        members()

        self.assertFalse(self.show_members.called)
        self.attempt_join_meshnet.assert_called_once_with()
