from raptiformica.settings.load import get_config
from tests.testcase import TestCase


class TestGetConfig(TestCase):
    def setUp(self):
        self.get_config_mapping = self.set_up_patch(
            'raptiformica.settings.load.get_config_mapping'
        )
        self.get_local_config_mapping = self.set_up_patch(
            'raptiformica.settings.load.get_local_config_mapping'
        )
        self.dictionary_map = self.set_up_patch(
            'raptiformica.settings.load.dictionary_map'
        )

    def test_get_config_gets_config_mapping(self):
        get_config()

        self.get_config_mapping.assert_called_once_with()

    def test_get_config_does_not_get_local_config_mapping(self):
        get_config()

        self.assertFalse(self.get_local_config_mapping.called)

    def test_get_config_gets_local_config_mapping_if_cached(self):
        get_config(cached=True)

        self.get_local_config_mapping.assert_called_once_with()

    def test_get_config_does_not_get_config_mapping_if_cached(self):
        get_config(cached=True)

        self.assertFalse(self.get_config_mapping.called)

    def test_get_config_creates_dictionary_from_config_mapping(self):
        get_config()

        self.dictionary_map.assert_called_once_with(
            self.get_config_mapping.return_value
        )

    def test_get_config_creates_dictionary_from_cached_mapping_if_cached(self):
        get_config(cached=True)

        self.dictionary_map.assert_called_once_with(
            self.get_local_config_mapping.return_value
        )

    def test_get_config_returns_dictionary(self):
        ret = get_config()

        self.assertEqual(ret, self.dictionary_map.return_value)
