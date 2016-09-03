from raptiformica.settings.meshnet import ensure_shared_secret
from tests.testcase import TestCase


class TestEnsureSharedSecret(TestCase):
    def setUp(self):
        self.uuid = self.set_up_patch('raptiformica.settings.meshnet.uuid')
        self.uuid.uuid4.return_value.hex = 'a_generated_shared_secret'
        self.try_update_config = self.set_up_patch(
            'raptiformica.settings.meshnet.try_update_config'
        )
        self.get_config = self.set_up_patch('raptiformica.settings.meshnet.get_config')
        self.get_config.return_value = {
            'raptiformica/meshnet/consul/password': 'a_secret'
        }

    def test_ensure_shared_secret_does_not_update_secret_if_it_already_exists(self):
        ret = ensure_shared_secret('consul')

        self.assertEquals(ret, self.get_config.return_value)

    def test_ensure_shared_secret_generates_new_shared_secret_if_it_does_not_exist(self):
        self.get_config.return_value = {}

        ret = ensure_shared_secret('consul')

        self.try_update_config.assert_called_once_with({
            'raptiformica/meshnet/consul/password': 'a_generated_shared_secret'
        })
        self.assertEqual(ret, self.try_update_config.return_value)
