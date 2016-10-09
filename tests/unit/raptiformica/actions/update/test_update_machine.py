from mock import call

from raptiformica.actions.update import update_machine
from tests.testcase import TestCase


class TestUpdateMachine(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.actions.update.log'
        )
        self.get_first_server_type = self.set_up_patch(
            'raptiformica.actions.update.get_first_server_type'
        )
        self.provision_machine = self.set_up_patch(
            'raptiformica.actions.update.provision_machine'
        )

    def test_update_machine_logs_updating_machine_message(self):
        update_machine()

        self.assertTrue(self.log.info.called)

    def test_update_machine_gets_first_server_type_if_none_is_specified(self):
        update_machine()

        self.get_first_server_type.assert_called_once_with()

    def test_update_machine_does_not_get_first_server_type_if_specified(self):
        update_machine(server_type='headless')

        self.assertFalse(self.get_first_server_type.called)

    def test_update_machine_provisions_machine_as_the_specified_server_type(self):
        server_types = ('headless', 'workstation', 'htpc')
        for server_type in server_types:
            update_machine(server_type=server_type)

        expected_calls = map(
            lambda t: call(
                server_type=t
            ), server_types
        )
        self.assertCountEqual(
            self.provision_machine.mock_calls, expected_calls
        )
