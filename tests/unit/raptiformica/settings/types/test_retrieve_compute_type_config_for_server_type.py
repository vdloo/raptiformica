from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.types import retrieve_compute_type_config_for_server_type
from tests.testcase import TestCase


class TestRetrieveComputeTypeConfigForServerType(TestCase):
    def setUp(self):
        self.load_config = self.set_up_patch(
            'raptiformica.settings.types.load_config'
        )
        self.data = {
            'compute_types': {
                'docker': {'the': 'compute type config'}
            }
        }
        self.load_config.return_value = self.data
        self.verify_server_type_implemented_in_compute_type = self.set_up_patch(
            'raptiformica.settings.types.verify_server_type_implemented_in_compute_type'
        )

    def test_retrieve_compute_type_config_for_server_type_loads_mutable_config(self):
        retrieve_compute_type_config_for_server_type(
            server_type='headless', compute_type='docker'
        )

        self.load_config.assert_called_once_with(MUTABLE_CONFIG)

    def test_retrieve_compute_type_config_for_server_type_verifies_sever_type_implemented_in_compute_type(self):
        retrieve_compute_type_config_for_server_type(
            server_type='headless', compute_type='docker'
        )

        expected_compute_type_config = {'the': 'compute type config'}
        self.verify_server_type_implemented_in_compute_type.assert_called_once_with(
            expected_compute_type_config,
            'headless'
        )

    def test_retrieve_compute_type_config_for_server_type_returns_server_type_implementation_config(self):
        ret = retrieve_compute_type_config_for_server_type(
                server_type='headless', compute_type='docker'
        )

        self.assertEqual(
            ret, self.verify_server_type_implemented_in_compute_type.return_value
        )
