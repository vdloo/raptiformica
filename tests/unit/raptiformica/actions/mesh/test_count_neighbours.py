from raptiformica.actions.mesh import count_neighbours, CJDROUTE_CONF_PATH
from tests.testcase import TestCase


class TestCountNeighbours(TestCase):
    def setUp(self):
        self.get_config = self.set_up_patch(
            'raptiformica.actions.mesh.get_config_mapping'
        )
        self.load_json = self.set_up_patch(
            'raptiformica.actions.mesh.load_json'
        )
        self.load_json.return_value = {'publicKey': 'key3'}
        self.list_neighbours = self.set_up_patch(
            'raptiformica.actions.mesh.list_neighbours'
        )
        self.list_neighbours.return_value = [
            'key1',
            'key2',
            'key3',
            'key4',
            'key5'
        ]

    def test_count_neighbours_gets_config(self):
        count_neighbours()

        self.get_config.assert_called_once_with()

    def test_count_neighbours_loads_cjdroute_config(self):
        count_neighbours()

        self.load_json.assert_called_once_with(CJDROUTE_CONF_PATH)

    def test_count_neighbours_lists_all_cjdns_public_keys_from_mapping(self):
        count_neighbours()

        self.list_neighbours.assert_called_once_with(
            self.get_config.return_value
        )

    def test_count_neighbours_counts_public_keys_except_self(self):
        ret = count_neighbours()

        self.assertEqual(ret, 4)
