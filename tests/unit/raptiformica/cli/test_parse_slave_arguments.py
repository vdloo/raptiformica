from mock import call

from raptiformica.cli import parse_slave_arguments
from raptiformica.settings.server import get_server_types, get_first_server_type
from tests.testcase import TestCase


class TestParseSlaveArguments(TestCase):
    def setUp(self):
        self.argument_parser = self.set_up_patch('raptiformica.cli.ArgumentParser')
        self.parse_arguments = self.set_up_patch('raptiformica.cli.parse_arguments')

    def test_parse_slave_arguments_instantiates_argparser(self):
        parse_slave_arguments()

        self.argument_parser.assert_called_once_with(
            description='Provision and join a machine into the network'
        )

    def test_parse_slave_arguments_adds_arguments(self):
        parse_slave_arguments()

        expected_calls = [
            call('host', type=str, help='Hostname or ip of the machine'),
            call('--port', '-p', type=int, default=22,
                 help='Port to use to connect to the remote machine with over SSH'),
            call('--no-assimilate', action='store_true', default=False,
                 help='Only provision. Do not join or set up the distributed network.'),
            call('--server-type', type=str, default=get_first_server_type(),
                 choices=get_server_types(),
                 help='Specify a server type. Default is {}'.format( get_first_server_type())),
        ]
        self.assertEqual(
            self.argument_parser.return_value.add_argument.mock_calls,
            expected_calls
        )

    def test_parse_slave_arguments_parses_arguments(self):
        parse_slave_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_slave_arguments_returns_parsed_arguments(self):
        ret = parse_slave_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)

