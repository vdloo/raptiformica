from random import randint

from raptiformica.actions.mesh import check_if_port_available_factory
from tests.testcase import TestCase


class TestCheckIfPortAvailableFactory(TestCase):
    def setUp(self):
        self.check_nonzero_exit = self.set_up_patch(
            'raptiformica.actions.mesh.check_nonzero_exit'
        )

    def test_check_if_port_available_factory_creates_function_that_check_if_port_is_available(self):
        mock_port = randint(150, 65535)

        check_if_port_available_factory(mock_port)()

        self.check_nonzero_exit.assert_called_once_with(
            "netstat -tuna | grep {:d}".format(mock_port)
        )

    def test_check_if_port_available_factory_returns_true_if_port_available(self):
        self.check_nonzero_exit.return_value = False

        ret = check_if_port_available_factory(123)()

        self.assertTrue(ret)

    def test_check_if_port_available_factory_returns_false_if_port_not_available(self):
        self.check_nonzero_exit.return_value = True

        ret = check_if_port_available_factory(123)()

        self.assertFalse(ret)
