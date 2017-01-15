from raptiformica.actions.mesh import not_already_known_consul_neighbour
from tests.testcase import TestCase


class TestNotAlreadyKnownConsulNeighbour(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.check_nonzero_exit = self.set_up_patch(
            'raptiformica.actions.mesh.check_nonzero_exit'
        )

    def test_not_already_known_consul_neighbour_logs_checking_already_known_message(self):
        not_already_known_consul_neighbour('some_ipv6_address')

        self.assertIn('some_ipv6_address', self.log.info.call_args[0][0])

    def test_not_already_known_consul_neighbour_checks_consul_members_for_the_ipv6_address(self):
        not_already_known_consul_neighbour('some_ipv6_address')

        self.check_nonzero_exit.assert_called_once_with(
            'consul members | grep -v left | grep some_ipv6_address'
        )

    def test_not_already_known_consul_neighbour_returns_false_if_ipv6_address_found(self):
        self.check_nonzero_exit.return_value = True

        ret = not_already_known_consul_neighbour('some_ipv6_address')

        self.assertFalse(ret)

    def test_not_already_known_consul_neighbour_returns_true_if_ipv6_not_found_or_consul_members_failed(self):
        self.check_nonzero_exit.return_value = False

        ret = not_already_known_consul_neighbour('some_ipv6_address')

        self.assertTrue(ret)
