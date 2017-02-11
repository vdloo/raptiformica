from raptiformica.actions.prune import ensure_neighbour_removed_from_config_by_host
from tests.testcase import TestCase


class TestEnsureNeighbourRemovedFromConfigByHost(TestCase):
    def setUp(self):
        self._del_neighbour_by_key = self.set_up_patch(
            'raptiformica.actions.prune._del_neighbour_by_key'
        )

    def test_ensure_neighbour_removed_from_config_by_host_deleted_neighbour_by_host(self):
        ensure_neighbour_removed_from_config_by_host('1.2.3.4')

        self._del_neighbour_by_key.assert_called_once_with(
            'host', '1.2.3.4'
        )
