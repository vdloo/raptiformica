from os.path import expanduser

from mock import Mock, call

from raptiformica.cli import parse_arguments
from raptiformica.settings import CACHE_DIR
from tests.testcase import TestCase


class TestParseArguments(TestCase):
    def setUp(self):
        self.parser = Mock()
        self.setup_logging = self.set_up_patch('raptiformica.cli.setup_logging')
        self.set_cache_dir = self.set_up_patch('raptiformica.cli.set_cache_dir')

    def test_parse_arguments_adds_arguments(self):
        parse_arguments(self.parser)

        expected_calls = [
            call('--verbose', '-v', action='store_true'),
            call('--cache-dir', '-c', type=str,
                 help="Use a specified settings dir instead of "
                      "{}. Path is relative to "
                      "{}".format(CACHE_DIR, expanduser("~")),
                 default=CACHE_DIR)
        ]
        self.assertEqual(
            self.parser.add_argument.mock_calls,
            expected_calls
        )

    def test_parse_arguments_parses_arguments(self):
        parse_arguments(self.parser)

        self.parser.parse_args.assert_called_once_with()

    def test_parse_arguments_sets_up_logging(self):
        parse_arguments(self.parser)

        self.setup_logging.assert_called_once_with(
            debug=self.parser.parse_args.return_value.verbose
        )

    def test_parse_arguments_sets_cache_dir(self):
        parse_arguments(self.parser)

        self.set_cache_dir.assert_called_once_with(
            self.parser.parse_args.return_value.cache_dir
        )

    def test_parse_arguments_returns_arguments(self):
        ret = parse_arguments(self.parser)

        self.assertEqual(ret, self.parser.parse_args.return_value)
