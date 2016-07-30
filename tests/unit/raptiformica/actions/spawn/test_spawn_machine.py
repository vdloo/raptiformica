from raptiformica.actions.spawn import spawn_machine
from raptiformica.settings.types import get_first_compute_type
from raptiformica.settings.types import get_first_server_type
from tests.testcase import TestCase


class TestSpawnMachine(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.spawn.log')
        self.verify_ssh_agent_running = self.set_up_patch('raptiformica.actions.spawn.verify_ssh_agent_running')
        self.start_compute_type = self.set_up_patch('raptiformica.actions.spawn.start_compute_type')
        self.start_compute_type.return_value = ('127.0.0.1', 2222)
        self.slave_machine = self.set_up_patch('raptiformica.actions.spawn.slave_machine')

    def test_spawn_machine_logs_spawning_machine_message(self):
        spawn_machine()

        self.assertTrue(self.log.info.called)

    def test_spawn_machine_verifies_ssh_agent_running(self):
        spawn_machine()

        self.verify_ssh_agent_running.assert_called_once_with()

    def test_spawn_machine_starts_compute_type_with_default_server_type_and_compute_type(self):
        spawn_machine()

        self.start_compute_type.assert_called_once_with(
            server_type=get_first_server_type(),
            compute_type=get_first_compute_type()
        )

    def test_spawn_machine_does_not_slave_or_assimilate_machine_by_default(self):
        spawn_machine(provision=True)

    def test_spawn_machine_slaves_machine_as_default_server_type(self):
        spawn_machine(provision=True)

        self.slave_machine.assert_called_once_with(
            '127.0.0.1',
            port=2222,
            provision=True,
            assimilate=False,
            server_type=get_first_server_type()
        )

    def test_spawn_machine_starts_compute_type_with_provided_server_type_and_compute_type(self):
        spawn_machine(server_type='workstation', compute_type='docker')

        self.start_compute_type.assert_called_once_with(
            server_type='workstation',
            compute_type='docker'
        )

    def test_spawn_machine_slave_machine_with_provided_server_type(self):
        spawn_machine(server_type='workstation', compute_type='docker',
                      provision=True, assimilate=True)

        self.slave_machine.assert_called_once_with(
            '127.0.0.1',
            port=2222,
            provision=True,
            assimilate=True,
            server_type='workstation'
        )

