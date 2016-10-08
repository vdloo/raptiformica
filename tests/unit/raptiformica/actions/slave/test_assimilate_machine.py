from raptiformica.actions.slave import assimilate_machine
from tests.testcase import TestCase


class TestAssimilateMachine(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.slave.log')
        self.download_artifacts = self.set_up_patch('raptiformica.actions.slave.download_artifacts')
        self.update_meshnet_config = self.set_up_patch('raptiformica.actions.slave.update_meshnet_config')

    def test_assimilate_machine_logs_assimilating_machine_message(self):
        assimilate_machine('1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_assimilate_machine_downloads_artifacts(self):
        assimilate_machine('1.2.3.4', port=2222)

        self.download_artifacts.assert_called_once_with('1.2.3.4', port=2222)

    def test_assimilate_machine_updates_meshnet_config(self):
        assimilate_machine('1.2.3.4', port=2222)

        self.update_meshnet_config.assert_called_once_with(
            '1.2.3.4', port=2222,
            compute_checkout_uuid=None
        )

    def test_assimilate_machine_updates_meshnet_config_with_optional_uuid(self):
        assimilate_machine('1.2.3.4', port=2222, uuid='some_uuid_1234')

        self.update_meshnet_config.assert_called_once_with(
            '1.2.3.4', port=2222,
            compute_checkout_uuid='some_uuid_1234'
        )
