from raptiformica.cli import parse_mesh_arguments
from raptiformica.settings import conf
from tests.testcase import TestCase


class TestParseMeshArguments(TestCase):
    def setUp(self):
        self.argument_parser = self.set_up_patch('raptiformica.cli.ArgumentParser')
        self.parse_arguments = self.set_up_patch('raptiformica.cli.parse_arguments')

    def test_parse_mesh_arguments_instantiates_argparser(self):
        parse_mesh_arguments()

        self.argument_parser.assert_called_once_with(
            prog='raptiformica mesh',
            description='Deploy a mesh configuration based on the {} config '
                        'file on this machine and attempt to join '
                        'the distributed network'.format(conf().MUTABLE_CONFIG)
        )

    def test_parse_mesh_arguments_adds_arguments(self):
        parse_mesh_arguments()

        self.assertFalse(self.argument_parser.return_value.add_argument.called)

    def test_parse_mesh_arguments_parses_arguments(self):
        parse_mesh_arguments()

        self.parse_arguments.assert_called_once_with(self.argument_parser.return_value)

    def test_parse_mesh_arguments_returns_parsed_arguments(self):
        ret = parse_mesh_arguments()

        self.assertEqual(ret, self.parse_arguments.return_value)
