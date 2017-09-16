from functools import partial
from unittest.mock import call

from raptiformica.actions.clean import clean_local_state, LOCAL_STATE_DIRS
from tests.testcase import TestCase


class TestCleanLocalState(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.clean.log')
        self.rmtree = self.set_up_patch('raptiformica.actions.clean.rmtree')

    def test_clean_local_state_logs_clean_local_state_message(self):
        clean_local_state()

        self.assertTrue(self.log.info.called)

    def test_clean_local_state_removes_all_state_paths_if_they_exist(self):
        clean_local_state()

        expected_calls = map(
            partial(call, ignore_errors=True), LOCAL_STATE_DIRS
        )
        self.assertCountEqual(self.rmtree.mock_calls, expected_calls)
