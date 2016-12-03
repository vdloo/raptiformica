from raptiformica.utils import group_n_elements
from tests.testcase import TestCase


class TestGroupNElements(TestCase):
    def setUp(self):
        self.testlist = [1, 2, 3, 4, 5, 6]

    def test_group_n_elements_groups_n_elements(self):
        ret = group_n_elements(self.testlist, 3)

        self.assertEqual(ret, [[1, 2, 3], [4, 5, 6]])

    def test_group_n_elements_also_groups_leftovers(self):
        ret = group_n_elements(self.testlist, 4)

        self.assertEqual(ret, [[1, 2, 3, 4], [5, 6]])
