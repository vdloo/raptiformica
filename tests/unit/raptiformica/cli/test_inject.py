from raptiformica.cli import inject
from tests.testcase import TestCase


class TestInject(TestCase):
    def setUp(self):
        self.parse_inject_arguments = self.set_up_patch(
            'raptiformica.cli.parse_inject_arguments'
        )
        # patching the original functions instead of the functions in the scope
        # of cli.py because these are conditional imports and so the functions
        # won't be available to patch until the function that imports it is
        # evaluated.
        self.ensure_no_consul_running = self.set_up_patch(
            'raptiformica.actions.mesh.ensure_no_consul_running'
        )
        self.update_meshnet_config = self.set_up_patch(
            'raptiformica.settings.meshnet.update_meshnet_config'
        )
        self.attempt_join_meshnet = self.set_up_patch(
            'raptiformica.actions.mesh.attempt_join_meshnet'
        )

    def test_inject_parses_inject_arguments(self):
        inject()

        self.parse_inject_arguments.assert_called_once_with()

    def test_inject_ensures_no_consul_running(self):
        inject()

        self.ensure_no_consul_running.assert_called_once_with()

    def test_inject_updates_meshnet_config(self):
        inject()

        self.update_meshnet_config.assert_called_once_with(
            self.parse_inject_arguments.return_value.host,
            port=self.parse_inject_arguments.return_value.port
        )

    def test_inject_attempts_join_meshnet(self):
        inject()

        self.attempt_join_meshnet.assert_called_once_with()
