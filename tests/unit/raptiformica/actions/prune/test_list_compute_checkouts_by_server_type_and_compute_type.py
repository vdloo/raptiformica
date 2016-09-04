from mock import call
from raptiformica.actions.prune import list_compute_checkouts_by_server_type_and_compute_type
from tests.testcase import TestCase


class TestListComputeCheckoutsByServerTypeAndComputeType(TestCase):
    def setUp(self):
        self.list_compute_checkouts_for_server_type_of_compute_type = self.set_up_patch(
            'raptiformica.actions.prune.list_compute_checkouts_for_server_type_of_compute_type'
        )
        self.list_compute_checkouts_for_server_type_of_compute_type.return_value = [{}, {}]
        self.get_compute_types = self.set_up_patch('raptiformica.actions.prune.get_compute_types')
        self.get_compute_types.return_value = ['vagrant', 'docker']
        self.get_server_types = self.set_up_patch('raptiformica.actions.prune.get_server_types')
        self.get_server_types.return_value = ['headless', 'workstation']

    def test_list_compute_checkouts_by_server_type_and_compute_type_lists_all_checkouts(self):
        list_compute_checkouts_by_server_type_and_compute_type()

        expected_calls = [
            call('headless', 'vagrant'),
            call('workstation', 'vagrant'),
            call('headless', 'docker'),
            call('workstation', 'docker'),
        ]
        self.assertCountEqual(
            self.list_compute_checkouts_for_server_type_of_compute_type.mock_calls,
            expected_calls
        )

    def test_list_compute_checkouts_by_server_type_and_compute_type_returns_compute_checkouts(self):
        ret = list_compute_checkouts_by_server_type_and_compute_type()

        self.assertCountEqual(
            ret,
            [{}] * 8
        )
