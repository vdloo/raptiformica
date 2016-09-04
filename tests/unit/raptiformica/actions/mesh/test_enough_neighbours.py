from raptiformica.actions.mesh import enough_neighbours
from tests.testcase import TestCase


class TestEnoughNeighbours(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.get_config = self.set_up_patch('raptiformica.actions.mesh.get_config')
        self.parse_cjdns_neighbours = self.set_up_patch('raptiformica.actions.mesh.parse_cjdns_neighbours')
        self.parse_cjdns_neighbours.return_value = []

    def test_enough_neighbours_logs_checking_enough_neighbours_message(self):
        enough_neighbours()

        self.assertTrue(self.log.info.called)

    def test_enough_neighbours_calls_parse_enough_neighbours_with_retrieved_mapping(self):
        enough_neighbours()

        self.parse_cjdns_neighbours.assert_called_once_with(self.get_config.return_value)

    def test_enough_neighbours_warns_not_enough_neighbours_when_no_neighbours(self):
        enough_neighbours()

        self.assertTrue(self.log.warning.called)

    def test_enough_neighbours_warns_not_enough_neighbours_when_one_neighbour(self):
        self.parse_cjdns_neighbours.return_value = [{}]

        enough_neighbours()

        self.assertTrue(self.log.warning.called)

    def test_enough_neighbours_does_not_warn_not_enough_neighbours_when_two_neighbours(self):
        self.parse_cjdns_neighbours.return_value = [{}, {}]

        enough_neighbours()

        self.assertFalse(self.log.warning.called)

    def test_enough_neighbours_returns_true_if_enough_neighbours(self):
        self.parse_cjdns_neighbours.return_value = [{}, {}]

        ret = enough_neighbours()

        self.assertTrue(ret)

    def test_enough_neighbours_returns_false_if_not_enough_neighbours(self):
        self.parse_cjdns_neighbours.return_value = []

        ret = enough_neighbours()

        self.assertFalse(ret)
