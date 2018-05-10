from mock import call, ANY

from raptiformica.cli import parse_deploy_arguments
from tests.testcase import TestCase


class TestParseDeployArguments(TestCase):
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

    def test_parse_deploy_arguments_instantiates_argparser(self):
        parse_deploy_arguments()

        self.argument_parser.assert_called_once_with(
            prog='raptiformica deploy',
            description='Set up or re-create an entire network based on a config file'
        )

    def test_parse_deploy_arguments_adds_arguments(self):
        parse_deploy_arguments()

        expected_calls = [
            call('inventory', type=str, help=ANY),
            call('--server-type', type=str,
                 default=self.get_first_server_type.return_value,
                 choices=self.get_server_types.return_value,
                 help='Specify a server type. Default is {}'
                      ''.format(self.get_first_server_type.return_value)),
            call('--modules', help=ANY, nargs='+',
                 dest='modules', default=list()),
            call( '--concurrent', help=ANY,
                  type=int, default=5)
        ]
        self.assertEqual(
            self.argument_parser.return_value.add_argument.mock_calls,
            expected_calls
        )

    def test_parse_deploy_arguments_parses_arguments(self):
        parse_deploy_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_deploy_arguments_returns_parsed_arguments(self):
        ret = parse_deploy_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)

