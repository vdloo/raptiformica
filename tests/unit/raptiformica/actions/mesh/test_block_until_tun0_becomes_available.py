from raptiformica.actions.mesh import check_if_tun0_is_available, block_until_tun0_becomes_available, \
    WAIT_FOR_VIRTUAL_NETWORK_ADAPTER_TIMEOUT
from tests.testcase import TestCase


class TestBlockUntilTun0BecomesAvailable(TestCase):
    def setUp(self):
        self.wait = self.set_up_patch(
            'raptiformica.actions.mesh.wait'
        )

    def test_block_until_tun0_becomes_available_waits_by_polling_the_tun0_iface_for_a_nonzer_exit_code(self):
        block_until_tun0_becomes_available()

        self.wait.assert_called_once_with(
            check_if_tun0_is_available,
            timeout=WAIT_FOR_VIRTUAL_NETWORK_ADAPTER_TIMEOUT
        )
