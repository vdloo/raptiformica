from raptiformica.cli import parse_clean_arguments
from tests.testcase import TestCase


class TestParseCleanArguments(TestCase):
    def setUp(self):
        self.argument_parser = self.set_up_patch('raptiformica.cli.ArgumentParser')
        self.parse_arguments = self.set_up_patch('raptiformica.cli.parse_arguments')

    def test_parse_clean_arguments_instantiates_argparser(self):
        parse_clean_arguments()

        self.argument_parser.assert_called_once_with(
            prog='raptiformica clean',
            description="Clean up all local state if any"
        )

    def test_parse_clean_arguments_parses_arguments(self):
        parse_clean_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_clean_arguments_returns_parsed_arguments(self):
        ret = parse_clean_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)
