from mock import ANY

from raptiformica.actions.mesh import consul_shared_secret_changed, get_consul_password
from tests.testcase import TestCase


class TestConsulSharedSecretChanged(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.actions.mesh.log'
        )
        self.mapping = {
            "raptiformica/meshnet/cjdns/password": "a_secret",
            "raptiformica/meshnet/consul/password": "a_different_secret",
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_ipv6_address": "some_ipv6_address",
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_port": 4863,
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_public_key": "a_pubkey.k",
            "raptiformica/meshnet/neighbours/a_pubkey.k/host": "192.168.178.23",
            "raptiformica/meshnet/neighbours/a_pubkey.k/ssh_port": "2200",
            "raptiformica/meshnet/neighbours/a_pubkey.k/uuid": "eb442c6170694b12b277c9e88d714cf2",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_ipv6_address": "some_other_ipv6_address",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_port": 4863,
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_public_key": "a_different_pubkey.k",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/host": "192.168.178.24",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/ssh_port": "2201",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/uuid": "eb442c6170694b12b277c9e88d714cf1",
        }
        self.get_config_mapping = self.set_up_patch(
            'raptiformica.actions.mesh.get_config_mapping'
        )
        self.get_config_mapping.return_value = self.mapping
        self.get_consul_password = self.set_up_patch(
            'raptiformica.actions.mesh.get_consul_password'
        )
        self.get_consul_password.side_effect = get_consul_password
        self.check_nonzero_exit = self.set_up_patch(
            'raptiformica.actions.mesh.check_nonzero_exit'
        )
        self.check_nonzero_exit.return_value = False

    def test_consul_shared_secret_changed_logs_checking_keyring(self):
        consul_shared_secret_changed()

        self.log.info.assert_called_once_with(ANY)

    def test_consul_shared_secret_changed_gets_config_mapping(self):
        consul_shared_secret_changed()

        self.get_config_mapping.assert_called_once_with()

    def test_consul_shared_secret_changed_gets_consul_password_from_config_mapping(self):
        consul_shared_secret_changed()

        self.get_consul_password.assert_called_once_with(
            self.get_config_mapping.return_value
        )

    def test_consul_shared_secret_changed_checks_nonzero_exit_of_keyring_grep(self):
        consul_shared_secret_changed()

        self.check_nonzero_exit.assert_called_once_with(
            'grep a_different_secret /opt/consul/serf/local.keyring'
        )

    def test_consul_shared_secret_changed_sanitizes_garbage_shared_secret(self):
        self.get_consul_password.side_effect = None
        self.get_consul_password.return_value = '; rm -Rf /some/dir/\''

        consul_shared_secret_changed()

        self.check_nonzero_exit.assert_called_once_with(
            'grep \'; rm -Rf /some/dir/\'"\'"\'\' /opt/consul/serf/local.keyring'
        )

    def test_consul_shared_secret_changes_returns_false_if_zero(self):
        self.check_nonzero_exit.return_value = True

        ret = consul_shared_secret_changed()

        self.assertFalse(ret)

    def test_consul_shared_secret_changes_returns_true_if_non_zero(self):
        self.check_nonzero_exit.return_value = False

        ret = consul_shared_secret_changed()

        self.assertTrue(ret)
