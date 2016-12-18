from mock import call, ANY

from raptiformica.cli import parse_inject_arguments
from tests.testcase import TestCase


class TestParseInjectArguments(TestCase):
    def setUp(self):
        self.argument_parser = self.set_up_patch('raptiformica.cli.ArgumentParser')
        self.parse_arguments = self.set_up_patch('raptiformica.cli.parse_arguments')

    def test_parse_inject_arguments_instantiates_argparser(self):
        parse_inject_arguments()

        self.argument_parser.assert_called_once_with(
            prog='raptiformica inject',
            description="Add a host to the local meshnet config"
        )

    def test_parse_inject_arguments_adds_arguments(self):
        parse_inject_arguments()

        expected_calls = [
            call('host', type=str, help='The host to add'),
            call('--port', '-p', type=int, default=22, help=ANY),
        ]
        self.assertEqual(
            self.argument_parser.return_value.add_argument.mock_calls,
            expected_calls
        )

    def test_parse_inject_arguments_parses_arguments(self):
        parse_inject_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_inject_arguments_returns_parsed_arguments(self):
        ret = parse_inject_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)
