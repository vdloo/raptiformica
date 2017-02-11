from raptiformica.actions.prune import ensure_neighbour_removed_from_config_by_uuid
from tests.testcase import TestCase


class TestEnsureNeighbourRemovedFromConfigByUuid(TestCase):
    def setUp(self):
        self._del_neighbour_by_key = self.set_up_patch(
            'raptiformica.actions.prune._del_neighbour_by_key'
        )

    def test_ensure_neighbour_removed_from_config_by_uuid_deleted_neighbour_by_uuid(self):
        ensure_neighbour_removed_from_config_by_uuid('some_uuid')

        self._del_neighbour_by_key.assert_called_once_with(
            'uuid', 'some_uuid'
        )
