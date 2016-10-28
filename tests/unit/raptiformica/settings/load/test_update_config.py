from raptiformica.settings.load import update_config_mapping
from tests.testcase import TestCase


class TestUpdateConfig(TestCase):
    def setUp(self):
        self.mapping = {
            'some/key': 'some_value',
            'some/other/key': 'some_other_value'
        }
        self.upload_config = self.set_up_patch(
            'raptiformica.settings.load.upload_config_mapping'
        )
        self.download_config = self.set_up_patch(
            'raptiformica.settings.load.download_config_mapping'
        )

    def test_update_config_uploads_mapping(self):
        update_config_mapping(self.mapping)

        self.upload_config.assert_called_once_with(self.mapping)

    def test_update_config_downloads_config(self):
        update_config_mapping(self.mapping)

        self.download_config.assert_called_once_with()

    def test_update_config_returns_updated_config(self):
        ret = update_config_mapping(self.mapping)

        self.assertEqual(
            ret, self.download_config.return_value
        )
