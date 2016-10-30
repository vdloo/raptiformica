from os.path import join

from raptiformica.settings import INSTALL_DIR
from raptiformica.shell.git import ensure_latest_source
from tests.testcase import TestCase


class TestEnsureLatestSource(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.git.log')
        self.run_command = self.set_up_patch('raptiformica.shell.git.run_command')
        self.run_command.return_value = (0, 'standard out output', None)
        self.ensure_latest_source_success_factory = self.set_up_patch(
            'raptiformica.shell.git.ensure_latest_source_success_factory'
        )
        self.ensure_latest_source_failure_factory = self.set_up_patch(
            'raptiformica.shell.git.ensure_latest_source_failure_factory'
        )

    def test_ensure_latest_source_logs_ensuring_latest_source_message(self):
        ensure_latest_source(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22
        )

        self.assertTrue(self.log.info.called)

    def test_ensure_latest_source_creates_ensure_latest_source_success_callback(self):
        ensure_latest_source(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22
        )

        self.ensure_latest_source_success_factory.assert_called_once_with(
            '/usr/etc/puppetfiles',
            host='1.2.3.4', port=22
        )

    def test_ensure_latest_source_creates_ensure_latest_source_failure_callback(self):
        ensure_latest_source(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22
        )

        self.ensure_latest_source_failure_factory.assert_called_once_with(
            "https://github.com/vdloo/puppetfiles",
            '/usr/etc/puppetfiles',
            host='1.2.3.4', port=22
        )

    def test_ensure_latest_source_runs_directory_exists_command(self):
        ensure_latest_source(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22,
        )

        expected_command = ['test', '-d', '/usr/etc/puppetfiles']
        self.run_command.assert_called_once_with(
            expected_command,
            host='1.2.3.4', port=22,
            success_callback=self.ensure_latest_source_success_factory.return_value,
            failure_callback=self.ensure_latest_source_failure_factory.return_value
        )

    def test_ensure_latest_source_returns_directory_status_exit_code(self):
        ret = ensure_latest_source(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22,
        )

        self.assertEqual(ret, 0)

    def test_ensure_latest_source_creates_success_callback_with_default_provisioning_directory(self):
        ensure_latest_source(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22
        )

        self.ensure_latest_source_success_factory.assert_called_once_with(
            join(INSTALL_DIR, 'puppetfiles'), host='1.2.3.4', port=22
        )

    def test_ensure_latest_source_creates_failure_callback_with_default_provisioning_directory(self):
        ensure_latest_source(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22
        )

        self.ensure_latest_source_failure_factory.assert_called_once_with(
            "https://github.com/vdloo/puppetfiles",
            join(INSTALL_DIR, 'puppetfiles'), host='1.2.3.4', port=22
        )

    def test_ensure_latest_source_creates_success_callback_with_specified_provisioning_directory(self):
        ensure_latest_source(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22,
            destination='/tmp/some/directory'
        )

        self.ensure_latest_source_success_factory.assert_called_once_with(
            '/tmp/some/directory/puppetfiles', host='1.2.3.4', port=22
        )

    def test_ensure_latest_source_creates_failure_callback_with_specified_provisioning_directory(self):
        ensure_latest_source(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22,
            destination='/tmp/some/directory'
        )

        self.ensure_latest_source_failure_factory.assert_called_once_with(
            "https://github.com/vdloo/puppetfiles",
            '/tmp/some/directory/puppetfiles', host='1.2.3.4', port=22
        )
