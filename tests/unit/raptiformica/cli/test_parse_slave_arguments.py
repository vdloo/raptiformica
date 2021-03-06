from mock import call

from raptiformica.cli import parse_slave_arguments
from tests.testcase import TestCase


class TestParseSlaveArguments(TestCase):
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

    def test_parse_slave_arguments_instantiates_argparser(self):
        parse_slave_arguments()

        self.argument_parser.assert_called_once_with(
            prog='raptiformica slave',
            description='Provision and join a machine into the network'
        )

    def test_parse_slave_arguments_adds_arguments(self):
        parse_slave_arguments()

        expected_calls = [
            call('host', type=str, help='Hostname or ip of the machine'),
            call('--port', '-p', type=int, default=22,
                 help='Port to use to connect to the remote machine with over SSH'),
            call('--no-provision', action='store_true', default=False,
                 help='Do not run the provisioning scripts for the specified server type'),
            call('--no-assimilate', action='store_true', default=False,
                 help='Do not join or set up the distributed network.'),
            call('--no-after-assimilate', action='store_true', default=False,
                 help='Do not perform the after assimilation hooks'),
            call('--no-after-mesh', action='store_true', default=False,
                 help='Do not perform the after mesh hooks'),
            call('--server-type', type=str, default=self.get_first_server_type.return_value,
                 choices=self.get_server_types.return_value,
                 help='Specify a server type. Default is {}'.format(self.get_first_server_type.return_value)),
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

