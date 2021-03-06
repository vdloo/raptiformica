from mock import Mock

from raptiformica.cli import spawn
from tests.testcase import TestCase


class TestSpawn(TestCase):
    def setUp(self):
        self.parse_spawn_arguments = self.set_up_patch(
            'raptiformica.cli.parse_spawn_arguments'
        )
        self.parse_spawn_arguments.return_value = Mock(
            no_provision=False, no_assimilate=False,
            no_after_assimilate=False, no_after_mesh=False,
            server_type='headless', compute_type='vagrant',
            check_available=False
        )
        self.spawn_machine = self.set_up_patch(
            'raptiformica.cli.spawn_machine'
        )

    def test_spawn_parses_spawn_arguments(self):
        spawn()

        self.parse_spawn_arguments.assert_called_once_with()

    def test_spawn_spawns_machines(self):
        spawn()

        self.spawn_machine.assert_called_once_with(
            provision=True, assimilate=True, after_assimilate=True,
            after_mesh=True, server_type='headless', compute_type='vagrant',
            only_check_available=False
        )

    def test_spawn_does_not_assimilate_machine_when_no_assimilate_is_passed(self):
        self.parse_spawn_arguments.return_value.no_assimilate = True

        spawn()

        self.spawn_machine.assert_called_once_with(
            provision=True, assimilate=False, after_assimilate=True,
            after_mesh=True, server_type='headless', compute_type='vagrant',
            only_check_available=False
        )

    def test_spawn_does_not_perform_after_assimilate_hooks_if_no_after_assimilate_is_passed(self):
        self.parse_spawn_arguments.return_value.no_after_assimilate = True

        spawn()

        self.spawn_machine.assert_called_once_with(
            provision=True, assimilate=True, after_assimilate=False,
            after_mesh=True, server_type='headless', compute_type='vagrant',
            only_check_available=False
        )

    def test_spawn_does_not_perform_after_mesh_hooks_if_no_after_mesh_is_passed(self):
        self.parse_spawn_arguments.return_value.no_after_mesh = True

        spawn()

        self.spawn_machine.assert_called_once_with(
            provision=True, assimilate=True, after_assimilate=True,
            after_mesh=False, server_type='headless', compute_type='vagrant',
            only_check_available=False
        )

    def test_spawn_dose_not_provision_machine_when_no_provision_is_passed(self):
        self.parse_spawn_arguments.return_value.no_provision = True

        spawn()

        self.spawn_machine.assert_called_once_with(
            provision=False, assimilate=True, after_assimilate=True,
            after_mesh=True, server_type='headless', compute_type='vagrant',
            only_check_available=False
        )

    def test_spawn_only_checks_available_if_specified(self):
        self.parse_spawn_arguments.return_value.check_available = True

        spawn()

        self.spawn_machine.assert_called_once_with(
            provision=True, assimilate=True, after_assimilate=True,
            after_mesh=True, server_type='headless', compute_type='vagrant',
            only_check_available=True
        )
