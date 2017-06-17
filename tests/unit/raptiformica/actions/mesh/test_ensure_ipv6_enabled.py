from mock import ANY

from raptiformica.actions.mesh import ensure_ipv6_enabled
from tests.testcase import TestCase


class TestEnsureIPv6Enabled(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.run_command_print_ready = self.set_up_patch(
            'raptiformica.actions.mesh.run_command_print_ready'
        )
        self.run_command_print_ready = self.set_up_patch(
            'raptiformica.actions.mesh.run_command_print_ready'
        )
        self.log_failure_factory = self.set_up_patch(
            'raptiformica.actions.mesh.log_failure_factory'
        )

    def test_ensure_ipv6_enabled_logs_info_message(self):
        ensure_ipv6_enabled()

        self.log.info.assert_called_once_with(ANY)

    def test_ensure_ipv6_enabled_configures_ipv6_not_disabled_at_kernel_level(self):
        ensure_ipv6_enabled()

        self.run_command_print_ready.assert_called_once_with(
            "/usr/bin/env sysctl net.ipv6.conf.all.disable_ipv6=0",
            failure_callback=self.log_failure_factory.return_value,
            shell=True,
            buffered=False
        )

    def test_ensure_ipv6_enabled_uses_log_failure_factory(self):
        ensure_ipv6_enabled()

        self.log_failure_factory.assert_called_once_with(ANY)
