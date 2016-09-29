from raptiformica.actions.mesh import check_if_tun0_is_available
from tests.testcase import TestCase


class TestCheckIfTun0IsAvailable(TestCase):
    def setUp(self):
        self.check_nonzero_exit_code = self.set_up_patch(
            'raptiformica.actions.mesh.check_nonzero_exit'
        )

    def test_check_if_tun0_is_available_checks_nonzero_exit_code_for_tun0_iface(self):
        check_if_tun0_is_available()

        self.check_nonzero_exit_code.assert_called_once_with(
            'ip addr show tun0'
        )

    def test_check_if_tun0_is_available_returns_check_tun0_exit_code(self):
        ret = check_if_tun0_is_available()

        self.assertEqual(ret, self.check_nonzero_exit_code.return_value)
