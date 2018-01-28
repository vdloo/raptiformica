from functools import partial
from unittest.mock import call
from tests.testcase import TestCase

from raptiformica.actions.mesh import remove_consul_local_state, CONSUL_STATE_DIRS


class TestRemoveConsulLocalState(TestCase):
    def setUp(self):
        self.rmtree = self.set_up_patch(
            'raptiformica.actions.mesh.rmtree'
        )

    def test_remove_consul_local_state_removes_tree_of_all_state_dirs(self):
        remove_consul_local_state()

        expected_calls = map(partial(call, ignore_errors=True), CONSUL_STATE_DIRS)
        self.assertCountEqual(expected_calls, self.rmtree.mock_calls)
