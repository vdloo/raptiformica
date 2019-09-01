from raptiformica.actions.prune import get_neighbours_by_host
from raptiformica.settings import conf
from tests.testcase import TestCase


class TestGetNeighboursByHost(TestCase):
    def setUp(self):
        self.get_config = self.set_up_patch(
            'raptiformica.actions.prune.get_config'
        )
        self.get_config.return_value = {
            conf().KEY_VALUE_PATH: {
                'meshnet': {
                    'neighbours': {
                        'neighbour_1.k': {
                            'uuid': 'eb442c6170694b12b277c9e88d714cf2',
                            'host': '1.2.3.4'
                        },
                        'neighbour_2.k': {
                            'uuid': 'eb442c6170694b12b277c9e88d714cf2',
                            'host': '1.2.3.4'
                        },
                        'neighbour_3.k': {
                            'uuid': 'eb442c6170694b12b277c9e88d712345',
                            'host': '1.2.3.6'
                        }
                    }
                }
            }
        }

    def test_get_neighbours_by_host_gets_config(self):
        get_neighbours_by_host('1.2.3.6')

        self.get_config.assert_called_once_with()

    def test_get_neighbours_by_host_returns_neighbour_root_key_if_one_match(self):
        ret = get_neighbours_by_host('1.2.3.6')

        expected_keys = (
            'raptiformica/meshnet/neighbours/neighbour_3.k/',  # trailing slash is important
        )
        self.assertCountEqual(ret, expected_keys)

    def test_get_neighbour_by_host_returns_neighbour_root_keys_if_two_matches(self):
        ret = get_neighbours_by_host('1.2.3.4')

        expected_keys = (
            'raptiformica/meshnet/neighbours/neighbour_1.k/',
            'raptiformica/meshnet/neighbours/neighbour_2.k/'
        )
        self.assertCountEqual(ret, expected_keys)

    def test_get_neighbour_by_host_returns_empty_iterable_if_no_matches(self):
        ret = get_neighbours_by_host('9.9.9.9')

        self.assertCountEqual(ret, tuple())

    def test_get_neighbours_by_host_returns_empty_iterable_if_no_neighbours(self):
        self.get_config.return_value = {
            conf().KEY_VALUE_PATH: {
                'meshnet': {}
            }
        }

        ret = get_neighbours_by_host('1.2.3.6')

        self.assertCountEqual(ret, tuple())

    def test_get_neighbours_by_host_returns_empty_iterable_if_no_meshnet_config(self):
        self.get_config.return_value = {
            conf().KEY_VALUE_PATH: {}
        }

        ret = get_neighbours_by_host('1.2.3.6')

        self.assertCountEqual(ret, tuple())
