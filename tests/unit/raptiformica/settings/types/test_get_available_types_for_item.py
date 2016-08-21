from mock import call

from raptiformica.settings.types import get_available_types_for_item
from tests.testcase import TestCase


class TestGetAvailableTypesForItem(TestCase):
    def setUp(self):
        self.list_types_from_config = self.set_up_patch(
            'raptiformica.settings.types.list_types_from_config'
        )
        self.list_types_from_config.return_value = [
            'docker', 'vagrant'
        ]
        self.check_type_available = self.set_up_patch(
            'raptiformica.settings.types.check_type_available'
        )

    def test_get_available_types_for_item_lists_all_types_from_config_for_item(self):
        get_available_types_for_item('compute_types')

        self.list_types_from_config.assert_called_once_with(
            'compute_types'
        )

    def test_get_available_types_for_item_checks_type_available_for_each_type(self):
        get_available_types_for_item('compute_types')

        expected_calls = [
            call('compute_types', 'docker'),
            call('compute_types', 'vagrant')
        ]
        self.assertCountEqual(self.check_type_available.mock_calls, expected_calls)
