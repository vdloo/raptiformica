from mock import ANY

from raptiformica.actions.mesh import consul_keyring_in_memory_is_stale
from tests.testcase import TestCase


class TestConsulKeyringInMemoryIsStale(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.actions.mesh.log'
        )
        self.check_nonzero_exit = self.set_up_patch(
            'raptiformica.actions.mesh.check_nonzero_exit'
        )
        self.check_nonzero_exit.return_value = False

    def test_consul_keyring_in_memory_is_stale_logs_checking_keyring_in_memory_message(self):
        consul_keyring_in_memory_is_stale('the_secret')

        self.log.info.assert_called_once_with(ANY)

    def test_consul_keyring_in_memory_is_stale_checks_if_shared_key_is_in_memory(self):
        consul_keyring_in_memory_is_stale('the_secret')

        self.check_nonzero_exit.assert_called_once_with(
            'if consul keyring -list > /dev/null; then consul keyring -list | '
            'grep -q the_secret; else /bin/true; fi'
        )

    def test_consul_keyring_in_memory_is_stale_escapes_special_characters_in_shared_secret(self):
        consul_keyring_in_memory_is_stale('\';echo 123 $%^"')

        self.check_nonzero_exit.assert_called_once_with(
            'if consul keyring -list > /dev/null; then consul keyring -list | '
            'grep -q \'\'"\'"\';echo 123 $%^"\'; else /bin/true; fi'
        )

    def test_consul_keyring_in_memory_is_stale_returns_true_if_returned_nonzero(self):
        ret = consul_keyring_in_memory_is_stale('the_secret')

        self.assertTrue(ret)

    def test_consul_keyring_in_memory_is_stale_returns_false_if_returned_zero(self):
        self.check_nonzero_exit.return_value = True

        ret = consul_keyring_in_memory_is_stale('the_secret')

        self.assertFalse(ret)
