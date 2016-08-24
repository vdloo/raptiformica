from raptiformica.cli import parse_prune_arguments
from tests.testcase import TestCase


class TestParsePruneArguments(TestCase):
    def setUp(self):
        self.argument_parser = self.set_up_patch('raptiformica.cli.ArgumentParser')
        self.parse_arguments = self.set_up_patch('raptiformica.cli.parse_arguments')

    def test_parse_prune_arguments_instantiates_argparser(self):
        parse_prune_arguments()

        self.argument_parser.assert_called_once_with(
            prog='raptiformica prune',
            description="Clean up inactive instances"
        )

    def test_parse_prune_arguments_adds_arguments(self):
        parse_prune_arguments()

        self.assertFalse(self.argument_parser.return_value.add_argument.called)

    def test_parse_prune_arguments_parses_arguments(self):
        parse_prune_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_prune_arguments_returns_parsed_arguments(self):
        ret = parse_prune_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)
