from raptiformica.settings.meshnet import retrieve_shared_secret
from tests.testcase import TestCase


class TestRetrieveSharedSecret(TestCase):
    def setUp(self):
        self.get_config_mapping = self.set_up_patch(
            'raptiformica.settings.meshnet.get_config_mapping'
        )
        self.sleep = self.set_up_patch(
            'raptiformica.settings.meshnet.sleep'
        )
        self.mapping = {
            'raptiformica/meshnet/cjdns/password': 'a_generated_shared_secret',
            'raptiformica/meshnet/consul/password': 'b_generated_shared_secret'
        }
        self.get_config_mapping.return_value = self.mapping

    def test_retrieve_shared_secret_gets_config_mapping(self):
        retrieve_shared_secret('consul', attempts=1)

        self.get_config_mapping.assert_called_once_with()

    def test_retrieve_shared_secret_returns_retrieved_mapping(self):
        ret = retrieve_shared_secret('consul', attempts=1)

        self.assertEqual(ret, self.mapping)

    def test_retrieve_shared_secret_returns_retrieved_mapping_if_missing_shared_secret(self):
        self.mapping = {
            'raptiformica/meshnet/cjdns/password': 'a_generated_shared_secret'
        }
        self.get_config_mapping.return_value = self.mapping

        ret = retrieve_shared_secret('consul', attempts=1)

        self.assertEqual(ret, self.mapping)

    def test_retrieve_shared_secret_does_not_sleep_if_missing_shared_secret(self):
        self.mapping = {
            'raptiformica/meshnet/cjdns/password': 'a_generated_shared_secret'
        }
        self.get_config_mapping.return_value = self.mapping

        retrieve_shared_secret('consul', attempts=1)

        self.assertFalse(self.sleep.called)

    def test_retrieve_shared_secret_retries_if_missing_shared_secret_and_attempts_left(self):
        self.mapping_with_missing_secret = {
            'raptiformica/meshnet/cjdns/password': 'a_generated_shared_secret'
        }
        self.get_config_mapping.side_effect = (
            self.mapping_with_missing_secret,
            self.mapping
        )

        ret = retrieve_shared_secret('consul', attempts=2)

        self.assertEqual(ret, self.mapping)

    def test_retrieve_shared_secret_sleeps_if_missing_shared_secret_and_attempt_left(self):
        self.mapping_with_missing_secret = {
            'raptiformica/meshnet/cjdns/password': 'a_generated_shared_secret'
        }
        self.get_config_mapping.side_effect = (
            self.mapping_with_missing_secret,
            self.mapping
        )

        retrieve_shared_secret('consul', attempts=2)

        self.sleep.assert_called_once_with(1)

    def test_retrieve_shared_secret_returns_mapping_with_missing_secret_if_attempts_ran_out(self):
        self.mapping_with_missing_secret = {
            'raptiformica/meshnet/cjdns/password': 'a_generated_shared_secret'
        }
        self.get_config_mapping.side_effect = (
            self.mapping_with_missing_secret,
            self.mapping_with_missing_secret,
            self.mapping
        )

        ret = retrieve_shared_secret('consul', attempts=2)

        self.assertEqual(ret, self.mapping_with_missing_secret)

    def test_retrieve_shared_secret_sleeps_once_with_missing_secret_if_attempts_ran_out(self):
        self.mapping_with_missing_secret = {
            'raptiformica/meshnet/cjdns/password': 'a_generated_shared_secret'
        }
        self.get_config_mapping.side_effect = (
            self.mapping_with_missing_secret,
            self.mapping_with_missing_secret,
            self.mapping
        )

        retrieve_shared_secret('consul', attempts=2)

        self.sleep.assert_called_once_with(1)

