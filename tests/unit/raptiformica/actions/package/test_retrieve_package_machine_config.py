from raptiformica.actions.package import retrieve_package_machine_config
from tests.testcase import TestCase


class TestRetrievePackageMachineConfig(TestCase):
    def setUp(self):
        self.get_first_server_type = self.set_up_patch(
            'raptiformica.actions.package.get_first_server_type'
        )
        self.get_first_server_type.return_value = 'headless'
        self.get_first_compute_type = self.set_up_patch(
            'raptiformica.actions.package.get_first_compute_type'
        )
        self.get_first_compute_type.return_value = 'vagrant'
        self.get_config = self.set_up_patch(
            'raptiformica.actions.package.get_config'
        )
        self.get_config.return_value = {
            'raptiformica': {
                'compute': {
                    'vagrant': {
                        'headless': {
                            'package': 'cd some/directory && ./package.sh'
                        }
                    }
                }
            }
        }

    def test_retrieve_package_machine_config_gets_first_server_type_if_no_server_type_specified(self):
        retrieve_package_machine_config()

        self.get_first_server_type.assert_called_once_with()

    def test_retrieve_package_machine_config_does_not_get_first_server_type_if_server_type_specified(self):
        retrieve_package_machine_config(server_type='headless')

        self.assertFalse(self.get_first_server_type.called)

    def test_retrieve_package_machine_config_gets_first_compute_type_if_no_compute_type_specified(self):
        retrieve_package_machine_config()

        self.get_first_compute_type.assert_called_once_with()

    def test_retrieve_package_machine_config_does_not_get_first_compute_type_if_compute_type_specified(self):
        retrieve_package_machine_config(compute_type='vagrant')

        self.assertFalse(self.get_first_compute_type.called)

    def test_retrieve_package_machine_config_gets_config(self):
        retrieve_package_machine_config()

        self.get_config.assert_called_once_with()

    def test_retrieve_package_machine_config_returns_package_command(self):
        ret = retrieve_package_machine_config()

        self.assertEqual(ret, 'cd some/directory && ./package.sh')

    def test_retrieve_package_machine_config_raises_error_when_no_such_server_type_configured(self):
        with self.assertRaises(RuntimeError):
            retrieve_package_machine_config(server_type='does_not_exist')

    def test_retrieve_package_machine_config_raises_error_when_no_such_compute_type_configured(self):
        with self.assertRaises(RuntimeError):
            retrieve_package_machine_config(compute_type='does_not_exist')

    def test_retrieve_package_machine_config_raises_error_when_no_package_command_configured(self):
        del self.get_config.return_value['raptiformica']['compute']['vagrant']['headless']['package']
        with self.assertRaises(RuntimeError):
            retrieve_package_machine_config()
