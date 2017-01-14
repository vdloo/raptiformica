from raptiformica.settings import conf
from raptiformica.settings.load import purge_config
from tests.testcase import TestCase


class TestPurgeConfig(TestCase):
    def setUp(self):
        self.purge_local_config_mapping = self.set_up_patch(
            'raptiformica.settings.load.purge_local_config_mapping'
        )
        self.rmtree = self.set_up_patch(
            'raptiformica.settings.load.rmtree'
        )

    def test_purge_config_purges_local_config_mapping(self):
        purge_config()

        self.purge_local_config_mapping.assert_called_once_with()

    def test_purge_config_does_not_purge_artifacts_or_modules(self):
        purge_config()

        self.assertFalse(self.rmtree.called)

    def test_purge_config_purges_artifacts_if_specified(self):
        purge_config(purge_artifacts=True)

        self.rmtree.assert_called_once_with(
            conf().USER_ARTIFACTS_DIR, ignore_errors=True
        )

    def test_purge_config_purges_modules_dir_if_specified(self):
        purge_config(purge_modules=True)

        self.rmtree.assert_called_once_with(
            conf().USER_MODULES_DIR, ignore_errors=True
        )
