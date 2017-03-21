from mock import Mock

from raptiformica.cli import join
from tests.testcase import TestCase


class TestJoin(TestCase):
    def setUp(self):
        self.parse_join_arguments = self.set_up_patch(
            'raptiformica.cli.parse_join_arguments'
        )
        self.parse_join_arguments.return_value = Mock(
            no_provision=False, no_assimilate=False, no_after_assimilate=False,
            no_after_mesh=False, host='1.2.3.4', port=22,
            server_type='headless'
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
            '1.2.3.4', port=22, provision=True,
            assimilate=True, after_assimilate=True,
            after_mesh=True, server_type='headless'
        )

    def test_join_does_not_assimilate_machine_when_no_assimilate_is_passed(self):
        self.parse_join_arguments.return_value.no_assimilate = True

        join()

        self.join_machine.assert_called_once_with(
            '1.2.3.4', port=22, provision=True,
            assimilate=False, after_assimilate=True,
            after_mesh=True, server_type='headless'
        )

    def test_join_does_not_perform_after_assimilate_hooks_when_no_after_assimilate_is_passed(self):
        self.parse_join_arguments.return_value.no_after_assimilate = True

        join()

        self.join_machine.assert_called_once_with(
            '1.2.3.4', port=22, provision=True,
            assimilate=True, after_assimilate=False,
            after_mesh=True, server_type='headless'
        )

    def test_join_does_not_perform_after_mesh_hooks_when_no_after_mesh_is_passed(self):
        self.parse_join_arguments.return_value.no_after_mesh = True

        join()

        self.join_machine.assert_called_once_with(
            '1.2.3.4', port=22, provision=True,
            assimilate=True, after_assimilate=True,
            after_mesh=False, server_type='headless'
        )

    def test_join_does_not_provision_machine_when_no_provision_is_passed(self):
        self.parse_join_arguments.return_value.no_provision = True

        join()

        self.join_machine.assert_called_once_with(
            '1.2.3.4', port=22, provision=False,
            assimilate=True, after_assimilate=True,
            after_mesh=True, server_type='headless'
        )
