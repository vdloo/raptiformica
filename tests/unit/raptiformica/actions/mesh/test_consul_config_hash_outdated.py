from mock import ANY
from uuid import uuid4
from tempfile import NamedTemporaryFile

from raptiformica.actions.mesh import consul_config_hash_outdated, write_consul_config_hash
from tests.testcase import TestCase


class TestConsulConfigHashOutdated(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.config_hash_file = NamedTemporaryFile()
        self.consul_config_file = NamedTemporaryFile()
        self.set_up_patch(
            'raptiformica.actions.mesh.CONSUL_CONF_HASH', self.config_hash_file.name
        )
        self.set_up_patch(
            'raptiformica.actions.mesh.CONSUL_CONF_PATH', self.consul_config_file.name
        )
        self.consul_config_file.write(
            # Write a random bytestring to the config file
            str(uuid4).encode('utf-8')
        )
        self.consul_config_file.flush()

    def test_consul_config_hash_outdated_logs_checking_up_to_date(self):
        consul_config_hash_outdated()

        self.log.info.assert_called_once_with(ANY)

    def test_consul_config_hash_outdated_returns_true_if_no_hash_saved_yet(self):
        self.set_up_patch('raptiformica.actions.mesh.isfile', return_value=False)

        ret = consul_config_hash_outdated()

        self.assertTrue(ret)

    def test_consul_config_hash_outdated_returns_false_if_hash_still_up_to_date(self):
        write_consul_config_hash()

        ret = consul_config_hash_outdated()

        self.assertFalse(ret)

    def test_consul_config_hash_outdated_returns_true_if_hash_no_longer_up_to_date(self):
        write_consul_config_hash()

        self.consul_config_file.write(
            # Write a random bytestring to the config file
            # again so the hash is no longer up to date
            str(uuid4).encode('utf-8')
        )
        self.consul_config_file.flush()

        ret = consul_config_hash_outdated()

        self.assertTrue(ret)
