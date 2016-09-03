from raptiformica.settings.meshnet import update_cjdns_config
from tests.testcase import TestCase


class TestUpdateCjdnsConfig(TestCase):
    def setUp(self):
        self.ensure_shared_secret = self.set_up_patch('raptiformica.settings.meshnet.ensure_shared_secret')

    def test_update_cjdns_config_ensures_cjdns_shared_secret_in_config(self):
        update_cjdns_config()

        self.ensure_shared_secret.assert_called_once_with('cjdns')

    def test_udpate_cjdns_config_returns_updated_config(self):
        ret = update_cjdns_config()

        self.assertEqual(ret, self.ensure_shared_secret.return_value)
