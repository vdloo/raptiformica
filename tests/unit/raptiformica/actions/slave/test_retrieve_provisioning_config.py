from raptiformica.actions.slave import retrieve_provisioning_config
from tests.testcase import TestCase


class TestRetrieveProvisioningConfig(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.actions.slave.log'
        )
        self.get_first_server_type = self.set_up_patch(
            'raptiformica.actions.slave.get_first_server_type'
        )
        self.get_first_server_type.return_value = 'workstation'
        self.get_config = self.set_up_patch(
            'raptiformica.actions.slave.get_config'
        )
        self.mapping = {
            "raptiformica/compute/vagrant/headless/get_port": "cd headless && vagrant ssh-config | grep Port | awk '{print $NF}'",
            "raptiformica/compute/vagrant/headless/source": "https://github.com/vdloo/vagrantfiles.git",
            "raptiformica/compute/vagrant/headless/start_instance": "cd headless && vagrant up",
            "raptiformica/server/headless/bootstrap": "./papply.sh manifests/headless.pp",
            "raptiformica/server/headless/name": "puppetfiles",
            "raptiformica/server/headless/source": "https://github.com/vdloo/puppetfiles.git"
        }
        self.get_config.return_value = self.mapping

    def test_retrieve_provisioning_config_logs_debug_message(self):
        retrieve_provisioning_config()

        self.assertTrue(self.log.debug.called)

    def test_retrieve_provisioning_config_gets_first_server_type(self):
        retrieve_provisioning_config()

        self.get_first_server_type.assert_called_once_with()

    def test_retrieve_provisioning_config_does_not_get_first_server_type_if_one_is_specified(self):
        retrieve_provisioning_config(server_type='headless')

        self.assertFalse(self.get_first_server_type.called)

    def test_retrieve_provisioning_config_returns_provisioning_config_for_specified_server_type(self):
        ret = retrieve_provisioning_config('headless')

        expected_config = (
            'https://github.com/vdloo/puppetfiles.git',
            'puppetfiles',
            './papply.sh manifests/headless.pp'
        )
        self.assertEqual(tuple(ret), expected_config)

    def test_retrieve_provisioning_config_returns_empty_config_if_no_such_server_type(self):
        ret = retrieve_provisioning_config()

        expected_config = tuple()
        self.assertCountEqual(ret, expected_config)
