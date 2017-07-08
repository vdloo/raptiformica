from raptiformica.settings.meshnet import ensure_shared_secret
from tests.testcase import TestCase


class TestEnsureSharedSecret(TestCase):
    def setUp(self):
        self.retrieve_shared_secret = self.set_up_patch(
            'raptiformica.settings.meshnet.retrieve_shared_secret'
        )
        self.set_new_shared_secret = self.set_up_patch(
            'raptiformica.settings.meshnet.set_new_shared_secret'
        )
        self.retrieve_shared_secret.return_value = {
            'raptiformica/meshnet/cjdns/password': 'a_generated_shared_secret',
            'raptiformica/meshnet/consul/password': 'b_generated_shared_secret'
        }

    def test_ensure_shared_secret_retrieves_shared_secret(self):
        ensure_shared_secret('consul')

        self.retrieve_shared_secret.assert_called_once_with('consul')

    def test_ensure_shared_secret_does_not_set_new_shared_secret_if_path_is_not_empty(self):
        ensure_shared_secret('consul')

        self.assertFalse(self.set_new_shared_secret.called)

    def test_ensure_shared_secret_sets_new_shared_secret_if_path_is_empty(self):
        self.retrieve_shared_secret.return_value = {
            'raptiformica/meshnet/cjdns/password': 'a_generated_shared_secret'
        }

        ensure_shared_secret('consul')

        self.set_new_shared_secret.assert_called_once_with('consul')

    def test_ensure_shared_secret_returns_retrieved_mapping_if_path_is_not_empty(self):
        ret = ensure_shared_secret('consul')

        self.assertEqual(ret, self.retrieve_shared_secret.return_value)

    def test_ensure_shared_secret_returns_updated_mapping_if_path_is_empty(self):
        self.retrieve_shared_secret.return_value = {
            'raptiformica/meshnet/cjdns/password': 'a_generated_shared_secret'
        }

        ret = ensure_shared_secret('consul')

        self.assertEqual(ret, self.set_new_shared_secret.return_value)
