from mock import call

from raptiformica.cli import parse_destroy_arguments
from tests.testcase import TestCase


class TestParseDestroyArguments(TestCase):
    def setUp(self):
        self.argument_parser = self.set_up_patch('raptiformica.cli.ArgumentParser')
        self.parse_arguments = self.set_up_patch('raptiformica.cli.parse_arguments')

    def test_parse_destroy_arguments_instantiates_argparser(self):
        parse_destroy_arguments()

        self.argument_parser.assert_called_once_with(
            prog='raptiformica destroy',
            description="Clean up the cluster"
        )

    def test_parse_destroy_arguments_adds_arguments(self):
        parse_destroy_arguments()

        expected_calls = [
            call(
                '--purge-artifacts', action='store_true',
                help='Remove all stored artifacts'
            ),
            call(
                '--purge-modules', action='store_true',
                help='Remove all loaded modules'
            )
        ]
        self.assertEqual(
            self.argument_parser.return_value.add_argument.mock_calls,
            expected_calls
        )

    def test_parse_destroy_arguments_parses_arguments(self):
        parse_destroy_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_destroy_arguments_returns_parsed_arguments(self):
        ret = parse_destroy_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)
