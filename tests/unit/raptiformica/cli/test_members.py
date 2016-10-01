from raptiformica.cli import members
from tests.testcase import TestCase


class TestMembers(TestCase):
    def setUp(self):
        self.parse_members_arguments = self.set_up_patch('raptiformica.cli.parse_members_arguments')
        self.parse_members_arguments.return_value.rejoin = False
        self.show_members = self.set_up_patch('raptiformica.cli.show_members')
        self.rejoin_members = self.set_up_patch('raptiformica.cli.rejoin_members')

    def test_members_parses_members_arguments(self):
        members()

        self.parse_members_arguments.assert_called_once_with()

    def test_members_shows_members(self):
        members()

        self.show_members.assert_called_once_with()
        self.assertFalse(self.rejoin_members.called)

    def test_members_rejoins_members_if_specified(self):
        self.parse_members_arguments.return_value.rejoin = True

        members()

        self.assertFalse(self.show_members.called)
        self.rejoin_members.assert_called_once_with()
