from raptiformica.actions.prune import prune_local_machines
from tests.testcase import TestCase


class TestPruneLocalMachines(TestCase):
    def setUp(self):
        self.list_compute_checkouts_by_server_type_and_compute_type = self.set_up_patch(
            'raptiformica.actions.prune.list_compute_checkouts_by_server_type_and_compute_type'
        )
        self.register_clean_up_triggers = self.set_up_patch(
            'raptiformica.actions.prune.register_clean_up_triggers'
        )
        self.fire_clean_up_triggers = self.set_up_patch(
            'raptiformica.actions.prune.fire_clean_up_triggers'
        )

    def test_prune_local_machines_lists_compute_checkouts_by_server_type_and_compute_type(self):
        prune_local_machines()

        self.list_compute_checkouts_by_server_type_and_compute_type.assert_called_once_with()

    def test_prune_local_machines_registers_clean_up_triggers(self):
        prune_local_machines()

        self.register_clean_up_triggers.assert_called_once_with(
            self.list_compute_checkouts_by_server_type_and_compute_type.return_value
        )

    def test_prune_local_machines_fires_clean_up_triggers(self):
        prune_local_machines()

        self.fire_clean_up_triggers.assert_called_once_with(
            self.register_clean_up_triggers.return_value
        )
