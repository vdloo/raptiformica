from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.types import get_compute_types
from tests.testcase import TestCase


class TestGetComputeTypes(TestCase):
    def setUp(self):
        self.load_config = self.set_up_patch('raptiformica.settings.types.load_config')
        self.compute_types = {'compute_types': {'vagrant': {}, 'docker': {}}}
        self.load_config.return_value = self.compute_types

    def test_get_compute_types_loads_config(self):
        get_compute_types()

        self.load_config.assert_called_once_with(MUTABLE_CONFIG)

    def test_get_compute_types_returns_list_of_compute_types(self):
        ret = get_compute_types()

        self.assertCountEqual(ret, ['vagrant', 'docker'])

    def test_get_compute_types_returns_empty_list_if_no_compute_types(self):
        self.load_config.return_value = {}

        ret = get_compute_types()

        self.assertCountEqual(ret, [])
