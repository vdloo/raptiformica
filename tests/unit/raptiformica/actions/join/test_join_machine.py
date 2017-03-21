from raptiformica.actions.join import join_machine
from tests.testcase import TestCase


class TestJoinMachine(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.actions.join.log'
        )
        self.get_first_server_type = self.set_up_patch(
            'raptiformica.actions.join.get_first_server_type'
        )
        self.get_first_server_type.return_value = 'headless'
        self.verify_local_ssh_running = self.set_up_patch(
            'raptiformica.actions.join.verify_local_ssh_running'
        )
        self.forward_local_port = self.set_up_patch(
            'raptiformica.actions.join.forward_local_port'
        )
        self.forward_local_port.return_value.__enter__ = lambda a: None
        self.forward_local_port.return_value.__exit__ = lambda a, b, c, d: None
        self.copy_id_from_remote = self.set_up_patch(
            'raptiformica.actions.join.copy_id_from_remote'
        )
        self.slave = self.set_up_patch('raptiformica.actions.join.slave')

    def test_join_machine_logs_info_messages(self):
        join_machine('1.2.3.4')

        self.assertTrue(self.log.info.called)

    def test_join_machine_gets_first_server_type(self):
        join_machine('1.2.3.4')

        self.get_first_server_type.assert_called_once_with()

    def test_join_machine_does_not_get_first_server_type_if_provided(self):
        join_machine('1.2.3.4', server_type='workstation')

        self.assertFalse(self.get_first_server_type.called)

    def test_join_machine_checks_if_there_is_a_local_ssh_server_running(self):
        join_machine('1.2.3.4')

        self.verify_local_ssh_running.assert_called_once_with()

    def test_join_machine_forwards_the_local_ssh_port_to_the_remote_machine(self):
        join_machine('1.2.3.4')

        self.forward_local_port.assert_called_once_with(
            '1.2.3.4', source_port=22,
            destination_port=3222,
            ssh_port=22
        )

    def test_join_machine_forwards_the_local_ssh_port_to_the_remote_machine_using_a_specified_port(self):
        join_machine('1.2.3.4', port=4321)

        self.forward_local_port.assert_called_once_with(
            '1.2.3.4', source_port=22,
            destination_port=3222,
            ssh_port=4321
        )

    def test_join_machine_allows_remote_server_to_access_the_local_machine_over_ssh(self):
        join_machine('1.2.3.4')

        self.copy_id_from_remote.assert_called_once_with(
            '1.2.3.4', ssh_port=22
        )

    def test_join_machine_allows_remote_server_to_access_the_local_machine_over_ssh_using_a_specified_port(self):
        join_machine('1.2.3.4', port=4321)

        self.copy_id_from_remote.assert_called_once_with(
            '1.2.3.4', ssh_port=4321
        )

    def test_join_machine_slaves_the_local_machine_from_the_remote_host_through_the_tunnel(self):
        join_machine('1.2.3.4')

        self.slave.assert_called_once_with(
            host_to_slave='127.0.0.1',
            host_to_slave_port=3222,
            host='1.2.3.4', port=22,
            server_type=self.get_first_server_type.return_value
        )

    def test_join_machine_slaves_the_local_machine_from_the_remote_host_using_the_specified_port(self):
        join_machine('1.2.3.4', port=4321)

        self.slave.assert_called_once_with(
            host_to_slave='127.0.0.1',
            host_to_slave_port=3222,
            host='1.2.3.4', port=4321,
            server_type=self.get_first_server_type.return_value
        )

    def test_join_machine_slaves_the_local_machine_from_the_remote_host_using_the_specified_server_type(self):
        join_machine('1.2.3.4', server_type='workstation')

        self.slave.assert_called_once_with(
            host_to_slave='127.0.0.1',
            host_to_slave_port=3222,
            host='1.2.3.4', port=22,
            server_type='workstation'
        )
