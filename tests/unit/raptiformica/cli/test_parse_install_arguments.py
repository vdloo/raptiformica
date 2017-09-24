from mock import call

from raptiformica.cli import parse_install_arguments
from tests.testcase import TestCase


class TestParseInstallArguments(TestCase):
    def setUp(self):
        self.argument_parser = self.set_up_patch('raptiformica.cli.ArgumentParser')
        self.parse_arguments = self.set_up_patch('raptiformica.cli.parse_arguments')

    def test_parse_install_arguments_instantiates_argparser(self):
        parse_install_arguments()

        self.argument_parser.assert_called_once_with(
            prog='raptiformica install',
            description="Load or unload a module into the system"
        )

    def test_parse_install_arguments_adds_arguments(self):
        parse_install_arguments()

        expected_calls = [
            call(
                'name',
                type=str,
                help='Name of the module to load or unload. '
                     'Like "vdloo/raptiformica-map"'
            ),
            call(
                '--remove', '-r', action='store_true',
                help='Unload the module'
            )
        ]
        self.assertEqual(
            self.argument_parser.return_value.add_argument.mock_calls,
            expected_calls
        )

    def test_parse_install_arguments_parses_arguments(self):
        parse_install_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_install_arguments_returns_parsed_arguments(self):
        ret = parse_install_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)
