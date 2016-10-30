from mock import call
from raptiformica.cli import parse_ssh_arguments
from tests.testcase import TestCase


class TestParseSSHArguments(TestCase):
    def setUp(self):
        self.argument_parser = self.set_up_patch('raptiformica.cli.ArgumentParser')
        self.parse_arguments = self.set_up_patch('raptiformica.cli.parse_arguments')

    def test_parse_ssh_arguments_instantiates_argparser(self):
        parse_ssh_arguments()

        self.argument_parser.assert_called_once_with(
            prog='raptiformica ssh',
            description="SSH into one of the machines"
        )

    def test_parse_ssh_arguments_adds_arguments(self):
        parse_ssh_arguments()

        expected_calls = [
            call(
                '--info-only', '--only-info',
                action='store_true',
                help="Don't get a shell. Only print the command to connect."
            ),
        ]
        self.assertEqual(
            self.argument_parser.return_value.add_argument.mock_calls,
            expected_calls
        )

    def test_parse_ssh_arguments_parses_arguments(self):
        parse_ssh_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_ssh_arguments_returns_parsed_arguments(self):
        ret = parse_ssh_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)
