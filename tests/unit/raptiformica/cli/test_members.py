from raptiformica.cli import members
from tests.testcase import TestCase


class TestMembers(TestCase):
    def setUp(self):
        self.parse_members_arguments = self.set_up_patch('raptiformica.cli.parse_members_arguments')
        self.show_members = self.set_up_patch('raptiformica.cli.show_members')

    def test_members_parses_members_arguments(self):
        members()

        self.parse_members_arguments.assert_called_once_with()

    def test_members_shows_members(self):
        members()

        self.show_members.assert_called_once_with()
