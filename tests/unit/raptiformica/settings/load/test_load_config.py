from raptiformica.settings.load import load_config
from tests.testcase import TestCase


class TestLoadConfig(TestCase):
    def setUp(self):
        self.load_existing_config = self.set_up_patch(
            'raptiformica.settings.load.load_existing_config'
        )
        self.log = self.set_up_patch(
            'raptiformica.settings.load.log'
        )
        self.create_new_config = self.set_up_patch(
            'raptiformica.settings.load.create_new_config'
        )

    def test_load_config_loads_existing_config(self):
        load_config('/tmp/mutable_config.json')

        self.load_existing_config.assert_called_once_with(
            '/tmp/mutable_config.json', unresolved=False
        )

    def test_load_config_loads_unresolved_existing_config_if_specified(self):
        load_config('/tmp/mutable_config.json', unresolved=True)

        self.load_existing_config.assert_called_once_with(
            '/tmp/mutable_config.json', unresolved=True
        )

    def test_load_config_logs_warning_when_existing_config_could_not_be_loaded(self):
        self.load_existing_config.side_effect = OSError

        load_config('/tmp/mutable_config.json')

        self.assertTrue(self.log.warning.called)

    def test_load_config_creates_new_config_if_existing_config_could_not_be_loaded(self):
        self.load_existing_config.side_effect = ValueError

        load_config('/tmp/mutable_config.json')

        self.create_new_config.assert_called_once_with(
            '/tmp/mutable_config.json'
        )

    def test_load_config_returns_newly_created_config_if_existing_config_could_not_be_loaded(self):
        self.load_existing_config.side_effect = OSError

        ret = load_config('/tmp/mutable_config.json')

        self.assertEqual(ret, self.create_new_config.return_value)
