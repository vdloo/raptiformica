from mock import call

from raptiformica.cli import parse_join_arguments
from tests.testcase import TestCase


class TestParseJoinArguments(TestCase):
    def setUp(self):
        self.argument_parser = self.set_up_patch('raptiformica.cli.ArgumentParser')
        self.parse_arguments = self.set_up_patch('raptiformica.cli.parse_arguments')
        self.get_first_server_type = self.set_up_patch(
            'raptiformica.cli.get_first_server_type'
        )
        self.get_first_server_type.return_value = 'headless'
        self.get_server_types = self.set_up_patch(
            'raptiformica.cli.get_server_types'
        )
        self.get_first_server_type.return_value = [
            self.get_first_server_type.return_value
        ]

    def test_parse_join_arguments_instantiates_argparser(self):
        parse_join_arguments()

        self.argument_parser.assert_called_once_with(
            prog='raptiformica join',
            description='Provision and join this machine into an existing network'
        )

    def test_parse_join_arguments_adds_arguments(self):
        parse_join_arguments()

        expected_calls = [
            call(
                'host',
                type=str,
                help='Hostname or ip of the remote machine '
                     'to use to slave this machine to'
            ),
            call('--port', '-p', type=int, default=22,
                 help='Port to use to connect to the remote machine with over SSH'),
            call('--server-type', type=str, default=self.get_first_server_type.return_value,
                 choices=self.get_server_types.return_value,
                 help='Specify a server type. Default is {}'.format(self.get_first_server_type.return_value)),
        ]
        self.assertEqual(
            self.argument_parser.return_value.add_argument.mock_calls,
            expected_calls
        )

    def test_parse_join_arguments_parses_arguments(self):
        parse_join_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_join_arguments_returns_parsed_arguments(self):
        ret = parse_join_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)

