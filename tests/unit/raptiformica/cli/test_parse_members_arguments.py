from mock import call

from raptiformica.cli import parse_members_arguments
from tests.testcase import TestCase


class TestParseMembersArguments(TestCase):
    def setUp(self):
        self.argument_parser = self.set_up_patch('raptiformica.cli.ArgumentParser')
        self.parse_arguments = self.set_up_patch('raptiformica.cli.parse_arguments')

    def test_parse_members_arguments_instantiates_argparser(self):
        parse_members_arguments()

        self.argument_parser.assert_called_once_with(
            prog='raptiformica members',
            description="Manage the members of the distributed network."
        )

    def test_parse_members_arguments_adds_arguments(self):
        parse_members_arguments()

        expected_calls = [
            call(
                '--rejoin', '-r',
                action='store_true',
                help="Attempt to (re)join all members found in the available config"
            ),
        ]
        self.assertEqual(
            self.argument_parser.return_value.add_argument.mock_calls,
            expected_calls
        )

    def test_parse_members_arguments_parses_arguments(self):
        parse_members_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_members_arguments_returns_parsed_arguments(self):
        ret = parse_members_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)
