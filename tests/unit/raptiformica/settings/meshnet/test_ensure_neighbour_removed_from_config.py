from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.meshnet import ensure_neighbour_removed_from_config
from tests.testcase import TestCase


class TestEnsureNeighbourRemovedFromConfig(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.settings.meshnet.log')
        self.load_config = self.set_up_patch('raptiformica.settings.meshnet.load_config')
        self.write_config = self.set_up_patch('raptiformica.settings.meshnet.write_config')
        self.config = {
            'meshnet': {
                'neighbours': {
                    'publicKey1': {
                        'uuid': 'some_uuid_5678'
                    },
                    'publicKey2': {
                        'uuid': 'some_uuid_9999'
                    }
                }
            }
        }
        self.load_config.return_value = self.config

    def test_ensure_neighbour_removed_from_config_logs_ensure_neighbour_removed_from_config_debug_message(self):
        ensure_neighbour_removed_from_config('some_uuid_1234')

        self.assertTrue(self.log.debug.called)

    def test_ensure_neighbours_removed_from_config_loads_mutable_config(self):
        ensure_neighbour_removed_from_config('some_uuid_1234')

        self.load_config.assert_called_once_with(MUTABLE_CONFIG)

    def test_ensure_neighbour_removed_from_config_does_not_alter_config_when_neighbour_not_in_config(self):
        ensure_neighbour_removed_from_config('some_uuid_1234')

        self.write_config.assert_called_once_with(self.config, MUTABLE_CONFIG)

    def test_ensure_neighbour_removed_from_config_removed_neighbour_from_config_by_uuid(self):
        ensure_neighbour_removed_from_config('some_uuid_5678')

        expected_config = {
            'meshnet': {
                'neighbours': {
                    'publicKey2': {
                        'uuid': 'some_uuid_9999'
                    }
                }
            }
        }
        self.write_config.assert_called_once_with(expected_config, MUTABLE_CONFIG)
