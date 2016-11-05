from mock import call

from raptiformica.cli import parse_package_arguments
from tests.testcase import TestCase


class TestParsePackageArguments(TestCase):
    def setUp(self):
        self.argument_parser = self.set_up_patch('raptiformica.cli.ArgumentParser')
        self.parse_arguments = self.set_up_patch('raptiformica.cli.parse_arguments')
        self.get_first_server_type = self.set_up_patch(
            'raptiformica.cli.get_first_server_type'
        )
        self.get_first_server_type.return_value = 'headless'
        self.get_first_compute_type = self.set_up_patch(
            'raptiformica.cli.get_first_compute_type'
        )
        self.get_first_compute_type.return_value = 'vagrant'
        self.get_server_types = self.set_up_patch(
            'raptiformica.cli.get_server_types'
        )
        self.get_server_types.return_value = [
            self.get_first_server_type.return_value
        ]
        self.get_compute_types = self.set_up_patch(
            'raptiformica.cli.get_compute_types'
        )
        self.get_compute_types.return_value = [
            self.get_first_compute_type.return_value
        ]

    def test_parse_package_arguments_instantiates_argparser(self):
        parse_package_arguments()

        self.argument_parser.assert_called_once_with(
            prog='raptiformica package',
            description='Package a compute type into a reusable image to speed up '
                        'booting instances'
        )

    def test_parse_package_arguments_adds_arguments(self):
        parse_package_arguments()

        expected_calls = [
            call('--server-type', type=str, default=self.get_first_server_type.return_value,
                 choices=self.get_server_types.return_value,
                 help='Specify a server type. Default is {}'.format(
                         self.get_first_server_type.return_value)),
            call('--compute-type', type=str, default=self.get_first_compute_type.return_value,
                 choices=self.get_compute_types.return_value,
                 help='Specify a compute type. Default is {}'.format(
                         self.get_first_compute_type.return_value)),
            call('--check-available', action='store_true',
                 help='Check if there is a configured server and compute type available on this host')
        ]
        self.assertEqual(
            self.argument_parser.return_value.add_argument.mock_calls,
            expected_calls
        )

    def test_parse_package_arguments_parses_arguments(self):
        parse_package_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_package_arguments_returns_parsed_arguments(self):
        ret = parse_package_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)
