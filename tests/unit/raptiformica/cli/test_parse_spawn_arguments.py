from mock import call

from raptiformica.cli import parse_spawn_arguments
from raptiformica.settings.types import get_server_types, get_first_server_type, get_first_compute_type, \
    get_compute_types
from tests.testcase import TestCase


class TestParseSpawnArguments(TestCase):
    def setUp(self):
        self.argument_parser = self.set_up_patch('raptiformica.cli.ArgumentParser')
        self.parse_arguments = self.set_up_patch('raptiformica.cli.parse_arguments')

    def test_parse_spawn_arguments_instantiates_argparser(self):
        parse_spawn_arguments()

        self.argument_parser.assert_called_once_with(
            description='Spawn a machine to slave and assimilate into the network'
        )

    def test_parse_spawn_arguments_adds_arguments(self):
        parse_spawn_arguments()

        expected_calls = [
            call('--no-provision', action='store_true', default=False,
                 help='Do not run the provisioning scripts for the specified server type'),
            call('--no-assimilate', action='store_true', default=False,
                 help='Do not join or set up the distributed network.'),
            call('--server-type', type=str, default=get_first_server_type(),
                 choices=get_server_types(),
                 help='Specify a server type. Default is {}'.format(get_first_server_type())),
            call('--compute-type', type=str, default=get_first_compute_type(),
                 choices=get_compute_types(),
                 help='Specify a compute type. Default is {}'.format(get_first_compute_type())),
        ]
        self.assertEqual(
            self.argument_parser.return_value.add_argument.mock_calls,
            expected_calls
        )

    def test_parse_spawn_arguments_parses_arguments(self):
        parse_spawn_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_spawn_arguments_returns_parsed_arguments(self):
        ret = parse_spawn_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)
