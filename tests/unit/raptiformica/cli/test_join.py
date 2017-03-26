from mock import Mock

from raptiformica.cli import join
from tests.testcase import TestCase


class TestJoin(TestCase):
    def setUp(self):
        self.parse_join_arguments = self.set_up_patch(
            'raptiformica.cli.parse_join_arguments'
        )
        self.parse_join_arguments.return_value = Mock(
            host='1.2.3.4', port=22, server_type='headless'
        )
        self.join_machine = self.set_up_patch(
            'raptiformica.cli.join_machine'
        )

    def test_join_parses_join_arguments(self):
        join()

        self.parse_join_arguments.assert_called_once_with()

    def test_join_joins_machines(self):
        join()

        self.join_machine.assert_called_once_with(
            '1.2.3.4', port=22, server_type='headless'
        )

