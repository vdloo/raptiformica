from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.meshnet import update_meshnet_config
from tests.testcase import TestCase


class TestUpdateMeshnetConfig(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.settings.meshnet.log')
        self.load_config = self.set_up_patch('raptiformica.settings.meshnet.load_config')
        self.update_cjdns_config = self.set_up_patch('raptiformica.settings.meshnet.update_cjdns_config')
        self.update_consul_config = self.set_up_patch('raptiformica.settings.meshnet.update_consul_config')
        self.update_neighbours_config = self.set_up_patch('raptiformica.settings.meshnet.update_neighbours_config')
        self.write_config = self.set_up_patch('raptiformica.settings.meshnet.write_config')

    def test_update_meshnet_config_logs_updating_meshnet_config_message(self):
        update_meshnet_config('1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_update_meshnet_config_loads_mutable_config(self):
        update_meshnet_config('1.2.3.4', port=2222)

        self.load_config.assert_called_once_with(MUTABLE_CONFIG)

    def test_update_meshnet_updatess_cjdns_config(self):
        update_meshnet_config('1.2.3.4', port=2222)

        self.update_cjdns_config.assert_called_once_with(
            self.load_config.return_value
        )

    def test_update_meshnet_updates_consul_config(self):
        update_meshnet_config('1.2.3.4', port=2222)

        self.update_consul_config.assert_called_once_with(
            self.update_cjdns_config.return_value
        )

    def test_update_meshnet_updates_neighbours_config(self):
        update_meshnet_config('1.2.3.4', port=2222)

        self.update_neighbours_config.assert_called_once_with(
            self.update_consul_config.return_value,
            '1.2.3.4', port=2222
        )

    def test_update_meshnet_writes_updated_config_to_disk(self):
        update_meshnet_config('1.2.3.4', port=2222)

        self.write_config(
            self.update_neighbours_config.return_value,
            MUTABLE_CONFIG
        )

