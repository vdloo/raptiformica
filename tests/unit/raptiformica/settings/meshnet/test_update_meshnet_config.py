from raptiformica.settings.meshnet import update_meshnet_config
from tests.testcase import TestCase


class TestUpdateMeshnetConfig(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.settings.meshnet.log')
        self.update_cjdns_config = self.set_up_patch('raptiformica.settings.meshnet.update_cjdns_config')
        self.update_consul_config = self.set_up_patch('raptiformica.settings.meshnet.update_consul_config')
        self.update_neighbours_config = self.set_up_patch('raptiformica.settings.meshnet.update_neighbours_config')

    def test_update_meshnet_config_logs_updating_meshnet_config_message(self):
        update_meshnet_config('1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_update_meshnet_updatess_cjdns_config(self):
        update_meshnet_config('1.2.3.4', port=2222)

        self.update_cjdns_config.assert_called_once_with()

    def test_update_meshnet_updates_consul_config(self):
        update_meshnet_config('1.2.3.4', port=2222)

        self.update_consul_config.assert_called_once_with()

    def test_update_meshnet_updates_neighbours_config(self):
        update_meshnet_config('1.2.3.4', port=2222)

        self.update_neighbours_config.assert_called_once_with(
            '1.2.3.4', port=2222, uuid=None
        )

    def test_update_meshnet_updates_neighbours_config_with_optional_uuid(self):
        update_meshnet_config(
            '1.2.3.4', port=2222, compute_checkout_uuid='some_uuid_1234'
        )

        self.update_neighbours_config.assert_called_once_with(
            '1.2.3.4', port=2222, uuid='some_uuid_1234'
        )
