from raptiformica.actions.slave import assimilate_machine
from tests.testcase import TestCase


class TestAssimilateMachine(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.slave.log')
        self.download_artifacts = self.set_up_patch('raptiformica.actions.slave.download_artifacts')
        self.advertise = self.set_up_patch('raptiformica.actions.slave.advertise')
        self.ensure_route_to_new_neighbour = self.set_up_patch(
            'raptiformica.actions.slave.ensure_route_to_new_neighbour'
        )

    def test_assimilate_machine_logs_assimilating_machine_message(self):
        assimilate_machine('1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_assimilate_machine_downloads_artifacts(self):
        assimilate_machine('1.2.3.4', port=2222)

        self.download_artifacts.assert_called_once_with('1.2.3.4', port=2222)

    def test_assimilate_machine_sets_advertised_host_and_port_on_remote_machine(self):
        assimilate_machine('1.2.3.4', port=2222)

        self.advertise.assert_called_once_with('1.2.3.4', port=2222)

    def test_assimilate_machine_ensures_route_to_new_neighbour(self):
        assimilate_machine('1.2.3.4', port=2222)

        self.ensure_route_to_new_neighbour.assert_called_once_with(
            '1.2.3.4', port=2222,
            compute_checkout_uuid=None
        )

    def test_assimilate_machine_update_ensures_route_to_new_neighbour_with_optional_uuid(self):
        assimilate_machine('1.2.3.4', port=2222, uuid='some_uuid_1234')

        self.ensure_route_to_new_neighbour.assert_called_once_with(
            '1.2.3.4', port=2222,
            compute_checkout_uuid='some_uuid_1234'
        )
