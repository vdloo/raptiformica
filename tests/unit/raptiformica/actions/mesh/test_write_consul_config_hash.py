from mock import ANY
from tempfile import NamedTemporaryFile
from uuid import uuid4

from raptiformica.actions.mesh import write_consul_config_hash
from raptiformica.utils import calculate_checksum
from tests.testcase import TestCase


class TestWriteConsulConfigHash(TestCase):
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

    def tearDown(self):
        self.config_hash_file.close()
        self.consul_config_file.close()

    def test_write_consul_config_hash_logs_writing_config_hash_message(self):
        write_consul_config_hash()

        self.log.info.assert_called_once_with(ANY)

    def test_write_consul_config_hash_writes_hash_of_consul_config(self):
        write_consul_config_hash()

        expected_hash = calculate_checksum(self.consul_config_file.name)
        written_hash = self.config_hash_file.read().decode('utf-8')

        self.assertEqual(expected_hash, written_hash)
