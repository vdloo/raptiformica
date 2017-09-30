from mock import ANY
from tempfile import NamedTemporaryFile
from uuid import uuid4

from raptiformica.actions.mesh import write_cjdroute_config_hash
from raptiformica.utils import calculate_lines_checksum
from tests.testcase import TestCase


class TestWriteCjdrouteConfigHash(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.config_hash_file = NamedTemporaryFile()
        self.cjdroute_config_file = NamedTemporaryFile()
        self.set_up_patch(
            'raptiformica.actions.mesh.CJDROUTE_CONF_HASH', self.config_hash_file.name
        )
        self.set_up_patch(
            'raptiformica.actions.mesh.CJDROUTE_CONF_PATH', self.cjdroute_config_file.name
        )
        self.uuid1, self.uuid2 = uuid4(), uuid4()
        self.uuid2 = uuid4()
        self.cjdroute_config_file.write(
            # Write a random bytestring to the config file
            "{}\n{}\n".format(self.uuid1, self.uuid2).encode('utf-8')
        )
        self.cjdroute_config_file.flush()

    def tearDown(self):
        self.config_hash_file.close()
        self.cjdroute_config_file.close()

    def test_write_cjdroute_config_hash_logs_writing_config_hash_message(self):
        write_cjdroute_config_hash()

        self.log.info.assert_called_once_with(ANY)

    def test_write_cjdroute_config_hash_writes_hash_of_cjdroute_config(self):
        write_cjdroute_config_hash()

        expected_hash = calculate_lines_checksum(self.cjdroute_config_file.name)
        written_hash = self.config_hash_file.read().decode('utf-8')

        self.assertEqual(expected_hash, written_hash)

    def test_write_cjdroute_config_hash_writes_hash_of_cjdroute_config_any_order(self):
        cjdroute_config_file = NamedTemporaryFile()
        self.set_up_patch(
            'raptiformica.actions.mesh.CJDROUTE_CONF_PATH', cjdroute_config_file.name
        )
        cjdroute_config_file.write(
            # Write the same bytestring but with lines in other order
            "{}\n{}\n".format(self.uuid2, self.uuid1).encode('utf-8')
        )
        write_cjdroute_config_hash()

        expected_hash = calculate_lines_checksum(cjdroute_config_file.name)
        written_hash = self.config_hash_file.read().decode('utf-8')

        self.assertEqual(expected_hash, written_hash)
