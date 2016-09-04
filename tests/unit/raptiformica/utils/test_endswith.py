from raptiformica.utils import endswith
from tests.testcase import TestCase


class TestEndsWith(TestCase):
    def setUp(self):
        self.endswith = endswith('test')

    def test_ends_with_returns_true_if_string_ends_with_test(self):
        self.assertTrue(self.endswith('this_is_a_test'))

    def test_ends_with_returns_false_if_string_does_not_end_with_test(self):
        self.assertFalse(self.endswith('this_is_an_assertion'))
