from raptiformica.settings.meshnet import update_consul_config
from tests.testcase import TestCase


class TestUpdateConsulConfig(TestCase):
    def setUp(self):
        self.ensure_shared_secret = self.set_up_patch('raptiformica.settings.meshnet.ensure_shared_secret')

    def test_update_consul_config_ensures_consul_shared_secret_in_config(self):
        update_consul_config()

        self.ensure_shared_secret.assert_called_once_with('consul')

    def test_udpate_consul_config_returns_updated_config(self):
        ret = update_consul_config()

        self.assertEqual(ret, self.ensure_shared_secret.return_value)

