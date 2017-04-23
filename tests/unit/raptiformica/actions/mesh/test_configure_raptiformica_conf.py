from unittest.mock import mock_open, ANY

from raptiformica.actions.mesh import configure_raptiformica_conf
from tests.testcase import TestCase


class TestConfigureRaptiformicaConf(TestCase):
    def setUp(self):
        self.exists = self.set_up_patch(
            'raptiformica.actions.mesh.path.exists'
        )
        self.exists.return_value = False
        self.mock_open = mock_open()
        self.set_up_patch('raptiformica.actions.mesh.open', self.mock_open)

    def test_configure_raptiformica_conf_checks_if_path_exists(self):
        configure_raptiformica_conf()

        self.exists.assert_called_once_with(
           '/etc/systemd/system/multi-user.target.wants'
        )

    def test_configure_raptiformica_conf_does_not_write_to_service_file(self):
        configure_raptiformica_conf()

        self.assertFalse(self.mock_open().write.called)

    def test_configure_conf_writes_to_service_file_if_systemd(self):
        self.exists.return_value = True

        configure_raptiformica_conf()

        self.mock_open().write.assert_called_once_with(
            ANY
        )
