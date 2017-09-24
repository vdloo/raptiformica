from functools import partial
from unittest.mock import mock_open, ANY, call

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
        self.run_command_print_ready = self.set_up_patch(
            'raptiformica.actions.mesh.run_command_print_ready'
        )

    def test_configure_raptiformica_conf_checks_if_path_exists(self):
        configure_raptiformica_conf()

        self.exists.assert_called_once_with(
           '/usr/lib/systemd/system/'
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

    def test_configure_conf_enables_oneshot_if_systemd_and_new_unit_file(self):
        self.exists.side_effect = (True, False)

        configure_raptiformica_conf()

        expected_calls = map(
            partial(call, shell=True, buffered=False),
            ("systemctl daemon-reload",
             "systemctl enable raptiformica")
        )
        self.assertCountEqual(
            expected_calls, self.run_command_print_ready.mock_calls
        )

    def test_configure_conf_does_not_enable_oneshot_if_systemd_and_existing_unit_file(self):
        self.exists.side_effect = (True, True)

        configure_raptiformica_conf()

        self.assertFalse(self.run_command_print_ready.called)
