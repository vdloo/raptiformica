from raptiformica.actions.slave import retrieve_provisioning_configs
from tests.testcase import TestCase


class TestRetrieveProvisioningConfigs(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.actions.slave.log'
        )
        self.get_first_server_type = self.set_up_patch(
            'raptiformica.actions.slave.get_first_server_type'
        )
        self.get_first_server_type.return_value = 'workstation'
        self.get_config = self.set_up_patch(
            'raptiformica.settings.load.get_config_mapping'
        )
        self.mapping = {
            "raptiformica/compute/vagrant/headless/get_port": "cd headless && vagrant ssh-config "
                                                              "| grep Port | awk '{print $NF}'",
            "raptiformica/compute/vagrant/headless/source": "https://github.com/vdloo/vagrantfiles",
            "raptiformica/compute/vagrant/headless/start_instance": "cd headless && vagrant up",
            "raptiformica/server/headless/puppetfiles/bootstrap": "./papply.sh manifests/headless.pp",
            "raptiformica/server/headless/puppetfiles/source": "https://github.com/vdloo/puppetfiles"
        }
        self.get_config.return_value = self.mapping

    def test_retrieve_provisioning_configs_logs_debug_message(self):
        retrieve_provisioning_configs()

        self.assertTrue(self.log.debug.called)

    def test_retrieve_provisioning_configs_gets_first_server_type(self):
        retrieve_provisioning_configs()

        self.get_first_server_type.assert_called_once_with()

    def test_retrieve_provisioning_configs_does_not_get_first_server_type_if_one_is_specified(self):
        retrieve_provisioning_configs(server_type='headless')

        self.assertFalse(self.get_first_server_type.called)

    def test_retrieve_provisioning_configs_returns_provisioning_config_for_specified_server_type(self):
        ret = retrieve_provisioning_configs('headless')

        expected_config = {
            'puppetfiles': {
                'bootstrap': './papply.sh manifests/headless.pp',
                'source': 'https://github.com/vdloo/puppetfiles'
            }
        }
        self.assertEqual(ret, expected_config)

    def test_retrieve_provisioning_configs_assumes_dir_exists_if_no_source(self):
        del self.mapping['raptiformica/server/headless/puppetfiles/source']

        ret = retrieve_provisioning_configs('headless')

        expected_config = {
            'puppetfiles': {
                'bootstrap': './papply.sh manifests/headless.pp',
                'source': None
            }
        }
        self.assertEqual(ret, expected_config)

    def test_retrieve_provisioning_configs_returns_multiple_configs_for_specified_server_type_if_multiple_configs(self):
        self.mapping.update({
            "raptiformica/server/headless/raptiformica-map/bootstrap": "./deploy.sh",
            "raptiformica/server/headless/raptiformica-map/source": "https://github.com/vdloo/raptiformica-map"
        })
        ret = retrieve_provisioning_configs('headless')

        expected_config = {
            'puppetfiles': {
                'bootstrap': './papply.sh manifests/headless.pp',
                'source': 'https://github.com/vdloo/puppetfiles'
            },
            'raptiformica-map': {
                'bootstrap': './deploy.sh',
                'source': 'https://github.com/vdloo/raptiformica-map'
            }
        }
        self.assertEqual(ret, expected_config)

    def test_retrieve_provisioning_configs_returns_empty_config_if_no_such_server_type(self):
        ret = retrieve_provisioning_configs()

        expected_config = tuple()
        self.assertCountEqual(ret, expected_config)
