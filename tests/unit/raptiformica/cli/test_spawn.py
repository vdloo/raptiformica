from mock import Mock

from raptiformica.cli import spawn
from tests.testcase import TestCase


class TestSpawn(TestCase):
    def setUp(self):
        self.parse_spawn_arguments = self.set_up_patch('raptiformica.cli.parse_spawn_arguments')
        self.parse_spawn_arguments.return_value = Mock(
            no_provision=False, no_assimilate=False,
            server_type='headless', compute_type='vagrant',
            check_available=False
        )
        self.spawn_machine = self.set_up_patch('raptiformica.cli.spawn_machine')

    def test_spawn_parses_spawn_arguments(self):
        spawn()

        self.parse_spawn_arguments.assert_called_once_with()

    def test_spawn_spawns_machines(self):
        spawn()

        self.spawn_machine.assert_called_once_with(
            provision=True, assimilate=True,
            server_type='headless', compute_type='vagrant',
            only_check_available=False
        )

    def test_spawn_does_not_assimilate_machine_when_no_assimilate_is_passed(self):
        self.parse_spawn_arguments.return_value = Mock(
            no_provision=False, no_assimilate=True,
            server_type='headless', compute_type='vagrant',
            check_available=False
        )

        spawn()

        self.spawn_machine.assert_called_once_with(
            provision=True, assimilate=False,
            server_type='headless', compute_type='vagrant',
            only_check_available=False
        )

    def test_spawn_dose_not_provision_machine_when_no_provision_is_passed(self):
        self.parse_spawn_arguments.return_value = Mock(
            no_provision=True, no_assimilate=False,
            server_type='headless', compute_type='vagrant',
            check_available=False
        )

        spawn()

        self.spawn_machine.assert_called_once_with(
            provision=False, assimilate=True,
            server_type='headless', compute_type='vagrant',
            only_check_available=False
        )

    def test_spawn_only_checks_available_if_specified(self):
        self.parse_spawn_arguments.return_value = Mock(
            no_provision=False, no_assimilate=False,
            server_type='headless', compute_type='vagrant',
            check_available=True
        )

        spawn()

        self.spawn_machine.assert_called_once_with(
            provision=True, assimilate=True,
            server_type='headless', compute_type='vagrant',
            only_check_available=True
        )
