from raptiformica.settings import KEY_VALUE_PATH
from raptiformica.settings.types import retrieve_compute_type_config_for_server_type
from tests.testcase import TestCase


class TestRetrieveComputeTypeConfigForServerType(TestCase):
    def setUp(self):
        self.get_first_server_type = self.set_up_patch(
            'raptiformica.settings.types.get_first_server_type'
        )
        self.get_first_server_type.return_value = 'workstation'
        self.get_first_compute_type = self.set_up_patch(
            'raptiformica.settings.types.get_first_compute_type'
        )
        self.get_first_compute_type.return_value = 'vagrant'
        self.get_config = self.set_up_patch(
            'raptiformica.settings.types.get_config'
        )
        self.get_config.return_value = {
            KEY_VALUE_PATH: {
                'compute': {
                    'vagrant': {
                        'workstation': {
                            'these_are': 'some_settings'
                        }
                    }
                }
            }
        }

    def test_retrieve_compute_type_config_for_server_type_gets_first_server_type(self):
        retrieve_compute_type_config_for_server_type()

        self.get_first_server_type.assert_called_once_with()

    def test_retrieve_compute_type_config_for_server_type_gets_first_compute_type(self):
        retrieve_compute_type_config_for_server_type()

        self.get_first_compute_type.assert_called_once_with()

    def test_retrieve_compute_type_config_for_server_type_does_not_get_first_server_type_if_one_is_specified(self):
        retrieve_compute_type_config_for_server_type(server_type='workstation')

        self.assertFalse(self.get_first_server_type.called)

    def test_retrieve_compute_type_config_for_server_type_does_not_get_first_compute_type_if_one_is_specified(self):
        retrieve_compute_type_config_for_server_type(compute_type='vagrant')

        self.assertFalse(self.get_first_compute_type.called)

    def test_retrieve_compute_type_config_for_server_type_gets_config(self):
        retrieve_compute_type_config_for_server_type()

        self.get_config.assert_called_once_with()

    def test_retrieve_compute_type_config_for_server_type_returns_config_for_server_type(self):
        ret = retrieve_compute_type_config_for_server_type(
            server_type='workstation', compute_type='vagrant'
        )

        self.assertEqual(ret, {'these_are': 'some_settings'})

    def test_retrieve_compute_type_config_for_server_type_raises_runtime_error_when_no_such_compute_type(self):
        with self.assertRaises(RuntimeError):
            retrieve_compute_type_config_for_server_type(compute_type='does_not_exist')

    def test_retrieve_compute_type_config_for_server_type_raises_runtime_error_when_no_such_server_type(self):
        with self.assertRaises(RuntimeError):
            retrieve_compute_type_config_for_server_type(server_type='does_not_exist')
