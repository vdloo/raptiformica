from raptiformica.actions.mesh import check_if_consul_is_available
from tests.testcase import TestCase


class TestCheckIfConsulIsAvailable(TestCase):
    def setUp(self):
        self.check_nonzero_exit_code = self.set_up_patch(
            'raptiformica.actions.mesh.check_nonzero_exit'
        )

    def test_check_if_consul_is_available_checks_nonzero_exit_code_for_consul_members(self):
        check_if_consul_is_available()

        self.check_nonzero_exit_code.assert_called_once_with(
            'consul members'
        )

    def test_check_if_consul_is_available_returns_check_consul_exit_code(self):
        ret = check_if_consul_is_available()

        self.assertEqual(ret, self.check_nonzero_exit_code.return_value)
