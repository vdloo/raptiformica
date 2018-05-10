from raptiformica.settings import conf
from raptiformica.settings.load import write_config_mapping
from tests.testcase import TestCase


class TestWriteConfigMapping(TestCase):
    def setUp(self):
        self.ensure_directory = self.set_up_patch(
            'raptiformica.settings.load.ensure_directory'
        )
        self.write_json = self.set_up_patch(
            'raptiformica.settings.load.write_json'
        )
        self.config_cache_lock = self.set_up_patch(
            'raptiformica.settings.load.config_cache_lock'
        )
        self.config_cache_lock.return_value.__exit__ = lambda a, b, c, d: None
        self.config_cache_lock.return_value.__enter__ = lambda a: None
        self.data = {
            'the': 'data'
        }

    def test_write_config_ensures_artifact_directory(self):
        write_config_mapping(self.data, 'a_config_file.json')

        # Even though we only need the ABS_CACHE_DIR to
        # exist here we still create the deeper level
        # artifacts dir because that will be required
        # later as well. TODO: find a better suited place
        # to ensure the artifacts directory or make it not
        # a hard requirement for download_artifacts
        self.ensure_directory.assert_called_once_with(
            conf().USER_ARTIFACTS_DIR
        )

    def test_write_config_gets_config_cache_lock(self):
        write_config_mapping(self.data, 'a_config_file.json')

        self.config_cache_lock.assert_called_once_with()

    def test_write_config_writes_json(self):
        write_config_mapping(self.data, 'a_config_file.json')

        self.write_json.assert_called_once_with(
            self.data,
            'a_config_file.json'
        )
