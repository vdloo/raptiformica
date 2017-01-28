from raptiformica.actions.mesh import remove_old_consul_keyring
from tests.testcase import TestCase


class TestRemoveOldConsulKeyring(TestCase):
    def setUp(self):
        self.remove = self.set_up_patch(
            'raptiformica.actions.mesh.remove'
        )

    def test_remove_old_consul_keyring_tries_to_remove_old_consul_keyring(self):
        remove_old_consul_keyring()

        self.remove.assert_called_once_with(
            '/opt/consul/serf/local.keyring'
        )

    def test_remove_old_consul_keyring_ignores_file_not_found(self):
        self.remove.side_effect = FileNotFoundError

        ret = remove_old_consul_keyring()

        self.assertIsNone(ret)

    def test_remove_old_consul_keyring_raises_other_errors(self):
        self.remove.side_effect = IOError

        with self.assertRaises(IOError):
            remove_old_consul_keyring()
