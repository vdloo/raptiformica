from raptiformica.utils import startswith
from tests.testcase import TestCase


class TestStartsWith(TestCase):
    def setUp(self):
        self.startswith = startswith('test')

    def test_starts_with_returns_true_if_string_starts_with_test(self):
        self.assertTrue(self.startswith('test_this_is_a_test'))

    def test_starts_with_returns_false_if_string_does_not_start_with_test(self):
        self.assertFalse(self.startswith('this_is_an_assertion'))
