from mock import ANY

from raptiformica.settings.meshnet import set_new_shared_secret
from tests.testcase import TestCase


class TestSetNewSharedSecret(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.settings.meshnet.log')
        self.uuid = self.set_up_patch('raptiformica.settings.meshnet.uuid')
        self.uuid.uuid4.return_value.hex = 'new_shared_secret'
        self.try_update_config = self.set_up_patch(
            'raptiformica.settings.meshnet.try_update_config_mapping'
        )

    def test_set_new_shared_secret_logs_info_message(self):
        set_new_shared_secret('consul')

        self.log.info.assert_called_once_with(ANY)

    def test_set_new_shared_secret_tries_updating_config_mapping_with_consul_secret(self):
        set_new_shared_secret('consul')

        self.try_update_config.assert_called_once_with(
            {'raptiformica/meshnet/consul/password': 'new_shared_secret'}
        )

    def test_set_new_shared_secret_tries_updating_config_mapping_with_cjdns_secret(self):
        set_new_shared_secret('cjdns')

        self.try_update_config.assert_called_once_with(
            {'raptiformica/meshnet/cjdns/password': 'new_shared_secret'}
        )

    def test_new_shared_secret_returns_updated_mapping(self):
        ret = set_new_shared_secret('some_service')

        self.assertEqual(ret, self.try_update_config.return_value)
