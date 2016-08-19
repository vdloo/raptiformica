from raptiformica.utils import config_equals
from tests.testcase import TestCase


class TestConfigEquals(TestCase):
    def setUp(self):
        self.config = {
            'key': [
                {'item1': 'value1'},
                {'item2': 'value2'},
                {'item3': 'value3'}
            ]
        }

    def test_config_equals_returns_true_if_config_equals_even_if_it_has_an_un_ordered_list_as_value(self):
        def check_config(config) :
            return config_equals(config, config)
        # check more than once because every time python
        # iterates over the list the order can be different
        compare_attempts = 5
        expected_assertions = map(check_config, [self.config] * compare_attempts)
        self.assertTrue(all(expected_assertions))
