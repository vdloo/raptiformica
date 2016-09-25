from raptiformica.actions.mesh import enough_neighbours
from tests.testcase import TestCase


class TestEnoughNeighbours(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.count_neighbours = self.set_up_patch('raptiformica.actions.mesh.count_neighbours')
        self.count_neighbours.return_value = 0

    def test_enough_neighbours_logs_checking_enough_neighbours_message(self):
        enough_neighbours()

        self.assertTrue(self.log.info.called)

    def test_enough_neighbours_calls_parse_enough_neighbours_with_retrieved_mapping(self):
        enough_neighbours()

        self.count_neighbours.assert_called_once_with()

    def test_enough_neighbours_warns_not_enough_neighbours_when_no_neighbours(self):
        enough_neighbours()

        self.assertTrue(self.log.warning.called)

    def test_enough_neighbours_warns_not_enough_neighbours_when_one_neighbour(self):
        self.count_neighbours.return_value = 1

        enough_neighbours()

        self.assertTrue(self.log.warning.called)

    def test_enough_neighbours_does_not_warn_not_enough_neighbours_when_two_neighbours(self):
        self.count_neighbours.return_value = 2

        enough_neighbours()

        self.assertFalse(self.log.warning.called)

    def test_enough_neighbours_returns_true_if_enough_neighbours(self):
        self.count_neighbours.return_value = 2

        ret = enough_neighbours()

        self.assertTrue(ret)

    def test_enough_neighbours_returns_false_if_not_enough_neighbours(self):
        self.count_neighbours.return_value = 0

        ret = enough_neighbours()

        self.assertFalse(ret)
