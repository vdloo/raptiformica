from mock import call

from raptiformica.cli import parse_hook_arguments
from tests.testcase import TestCase


class TestParseHookArguments(TestCase):
    def setUp(self):
        self.argument_parser = self.set_up_patch('raptiformica.cli.ArgumentParser')
        self.parse_arguments = self.set_up_patch('raptiformica.cli.parse_arguments')

    def test_parse_hook_arguments_instantiates_argparser(self):
        parse_hook_arguments()

        self.argument_parser.assert_called_once_with(
            prog='raptiformica hook',
            description="Run all handlers for a specific hook from the config"
        )

    def test_parse_hook_arguments_adds_arguments(self):
        parse_hook_arguments()

        expected_calls = [
            call(
                'name',
                type=str,
                help='Name of the hook to fire. '
                     'i.e. after_mesh or cluster_change'
            ),
        ]
        self.assertEqual(
                self.argument_parser.return_value.add_argument.mock_calls,
                expected_calls
        )

    def test_parse_hook_arguments_parses_arguments(self):
        parse_hook_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_hook_arguments_returns_parsed_arguments(self):
        ret = parse_hook_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)
