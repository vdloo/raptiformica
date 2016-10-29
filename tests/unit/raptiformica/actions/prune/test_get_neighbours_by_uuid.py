from raptiformica.actions.prune import get_neighbours_by_uuid
from raptiformica.settings import KEY_VALUE_PATH
from tests.testcase import TestCase


class TestGetNeighboursByUuid(TestCase):
    def setUp(self):
        self.get_config = self.set_up_patch(
            'raptiformica.actions.prune.get_config'
        )
        self.get_config.return_value = {
            KEY_VALUE_PATH: {
                'meshnet': {
                    'neighbours': {
                        'neighbour_1.k': {
                            'uuid': 'eb442c6170694b12b277c9e88d714cf2'
                        },
                        'neighbour_2.k': {
                            'uuid': 'eb442c6170694b12b277c9e88d714cf2'
                        },
                        'neighbour_3.k': {
                            'uuid': 'eb442c6170694b12b277c9e88d712345'
                        }
                    }
                }
            }
        }

    def test_get_neighbours_by_uuid_gets_config(self):
        get_neighbours_by_uuid('eb442c6170694b12b277c9e88d714cf2')

        self.get_config.assert_called_once_with()

    def test_get_neighbours_by_uuid_returns_neighbour_root_key_if_one_match(self):
        ret = get_neighbours_by_uuid('eb442c6170694b12b277c9e88d712345')

        expected_keys = (
            'raptiformica/meshnet/neighbours/neighbour_3.k/',  # trailing slash is important
        )
        self.assertCountEqual(ret, expected_keys)

    def test_get_neighbour_by_uuid_returns_neighbour_root_keys_if_two_matches(self):
        ret = get_neighbours_by_uuid('eb442c6170694b12b277c9e88d714cf2')

        expected_keys = (
            'raptiformica/meshnet/neighbours/neighbour_1.k/',
            'raptiformica/meshnet/neighbours/neighbour_2.k/'
        )
        self.assertCountEqual(ret, expected_keys)

    def test_get_neighbour_by_uuid_returns_empty_iterable_if_no_matches(self):
        ret = get_neighbours_by_uuid('does_not_exist')

        self.assertCountEqual(ret, tuple())

    def test_get_neighbour_by_uuid_raises_key_error_if_no_meshnet_configured(self):
        self.get_config.return_value = {}

        with self.assertRaises(KeyError):
            get_neighbours_by_uuid('eb442c6170694b12b277c9e88d714cf2')

    def test_get_neighbours_by_uuid_returns_empty_iterable_if_no_neighbours(self):
        self.get_config.return_value = {
            KEY_VALUE_PATH: {
                'meshnet': {}
            }
        }

        ret = get_neighbours_by_uuid('eb442c6170694b12b277c9e88d714cf2')

        self.assertCountEqual(ret, tuple())
