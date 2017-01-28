from raptiformica.actions.mesh import block_until_consul_port_is_free, WAIT_FOR_CONSUL_PORT_TIMEOUT
from raptiformica.settings import Config
from tests.testcase import TestCase


class TestBlockUntilConsulPortIsFree(TestCase):
    def setUp(self):
        self.wait = self.set_up_patch(
            'raptiformica.actions.mesh.wait'
        )
        self.check_if_port_available_factory = self.set_up_patch(
            'raptiformica.actions.mesh.check_if_port_available_factory'
        )

    def test_block_until_consul_port_is_free_checks_the_default_consul_port(self):
        block_until_consul_port_is_free()

        self.check_if_port_available_factory.assert_called_once_with(
            Config.CONSUL_DEFAULT_PORT
        )

    def test_block_until_consul_port_is_free_polls_for_nonzero_exit_code_on_port_available(self):
        block_until_consul_port_is_free()

        self.wait.assert_called_once_with(
            self.check_if_port_available_factory.return_value,
            timeout=WAIT_FOR_CONSUL_PORT_TIMEOUT
        )
