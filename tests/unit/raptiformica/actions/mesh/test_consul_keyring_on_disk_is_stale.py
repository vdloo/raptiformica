from mock import ANY

from raptiformica.actions.mesh import consul_keyring_on_disk_is_stale
from tests.testcase import TestCase


class TestConsulKeyringOnDiskIsStale(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.actions.mesh.log'
        )
        self.check_nonzero_exit = self.set_up_patch(
            'raptiformica.actions.mesh.check_nonzero_exit'
        )
        self.check_nonzero_exit.return_value = False

    def test_consul_keyring_on_disk_is_stale_logs_checking_keyring_on_disk_message(self):
        consul_keyring_on_disk_is_stale('the_secret')

        self.log.info.assert_called_once_with(ANY)

    def test_consul_keyring_on_disk_is_stale_checks_if_shared_key_is_on_disk(self):
        consul_keyring_on_disk_is_stale('the_secret')

        self.check_nonzero_exit.assert_called_once_with(
            'grep the_secret /opt/consul/serf/local.keyring'
        )

    def test_consul_keyring_on_disk_is_stale_escapes_special_characters_in_shared_secret(self):
        consul_keyring_on_disk_is_stale('\';echo 123 $%^"')

        self.check_nonzero_exit.assert_called_once_with(
            'grep \'\'"\'"\';echo 123 $%^"\' /opt/consul/serf/local.keyring'
        )

    def test_consul_keyring_on_disk_is_stale_returns_true_if_returned_nonzero(self):
        ret = consul_keyring_on_disk_is_stale('the_secret')

        self.assertTrue(ret)

    def test_consul_keyring_on_disk_is_stale_returns_false_if_returned_zero(self):
        self.check_nonzero_exit.return_value = True

        ret = consul_keyring_on_disk_is_stale('the_secret')

        self.assertFalse(ret)
