from raptiformica.actions.mesh import check_if_consul_is_available, block_until_consul_becomes_available, \
    WAIT_FOR_CONSUL_TIMEOUT
from tests.testcase import TestCase


class TestBlockUntilConsulBecomesAvailable(TestCase):
    def setUp(self):
        self.wait = self.set_up_patch(
            'raptiformica.actions.mesh.wait'
        )

    def test_block_until_consul_becomes_available_waits_by_polling_the_consul_members_for_a_nonzer_exit_code(self):
        block_until_consul_becomes_available()

        self.wait.assert_called_once_with(
            check_if_consul_is_available,
            timeout=WAIT_FOR_CONSUL_TIMEOUT
        )
