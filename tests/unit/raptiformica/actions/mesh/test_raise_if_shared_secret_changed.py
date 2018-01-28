from contextlib import suppress

from raptiformica.actions.mesh import raise_if_shared_secret_changed, ConsulSharedSecretChanged
from tests.testcase import TestCase


class TestRaiseIfSharedSecretChanged(TestCase):
    def setUp(self):
        self.consul_shared_secret_changed = self.set_up_patch(
            'raptiformica.actions.mesh.consul_shared_secret_changed'
        )
        self.consul_shared_secret_changed.return_value = False
        self.sleep = self.set_up_patch(
            'raptiformica.actions.mesh.sleep'
        )

    def test_raise_if_shared_secret_changed_checks_if_shared_secret_changed(self):
        raise_if_shared_secret_changed()

        self.consul_shared_secret_changed.assert_called_once_with()

    def test_raise_if_shared_secret_changed_does_not_sleep_if_not_changed(self):
        raise_if_shared_secret_changed()

        self.assertFalse(self.sleep.called)

    def test_raise_if_shared_secret_changed_sleeps_for_damping_if_changed(self):
        self.consul_shared_secret_changed.return_value = True

        with suppress(ConsulSharedSecretChanged):
            raise_if_shared_secret_changed()

        self.assertEqual(self.sleep.call_count, 15)

    def test_raise_if_shared_secret_changed_raises_exception_if_changed(self):
        self.consul_shared_secret_changed.return_value = True

        with self.assertRaises(ConsulSharedSecretChanged):
            raise_if_shared_secret_changed()

    def test_raise_if_shared_secret_changed_does_not_raise_if_problem_fixed_self(self):
        self.consul_shared_secret_changed.side_effect = [True] * 4 + [False]

        # Does not raise ConsulSharedSecretChanged
        raise_if_shared_secret_changed()
