from raptiformica.settings.types import get_first_compute_type
from tests.testcase import TestCase


class TestGetFirstComputeType(TestCase):
    def setUp(self):
        self.load_config = self.set_up_patch('raptiformica.settings.types.load_config')
        self.compute_types = {'compute_types': {'vagrant': {}, 'docker': {}}}
        self.load_config.return_value = self.compute_types

    def test_get_first_compute_type_raises_value_error_if_no_of_that_type_is_configured(self):
        self.load_config.return_value = {'compute_types': {}}

        with self.assertRaises(ValueError):
            get_first_compute_type()

    def test_get_first_compute_type_returns_first_compute_type(self):
        ret = get_first_compute_type()

        self.assertEqual(ret, 'docker')  # the types are sorted so docker comes before vagrant
