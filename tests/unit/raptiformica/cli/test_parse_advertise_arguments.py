from mock import call

from raptiformica.cli import parse_advertise_arguments
from tests.testcase import TestCase


class TestParseAdvertiseArguments(TestCase):
    def setUp(self):
        self.argument_parser = self.set_up_patch('raptiformica.cli.ArgumentParser')
        self.parse_arguments = self.set_up_patch('raptiformica.cli.parse_arguments')

    def test_parse_advertise_arguments_instantiates_argparser(self):
        parse_advertise_arguments()

        self.argument_parser.assert_called_once_with(
            prog='raptiformica advertise',
            description="Set the host and port to advertise on the local machine"
        )

    def test_parse_advertise_arguments_adds_arguments(self):
        parse_advertise_arguments()

        expected_calls = [
            call('host', type=str, help='The host to advertise'),
            call(
                '--port', '-p', type=int, default=22,
                help='The port to advertise'
            )
        ]
        self.assertEqual(
            self.argument_parser.return_value.add_argument.mock_calls,
            expected_calls
        )

    def test_parse_advertise_arguments_parses_arguments(self):
        parse_advertise_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_advertise_arguments_returns_parsed_arguments(self):
        ret = parse_advertise_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)
