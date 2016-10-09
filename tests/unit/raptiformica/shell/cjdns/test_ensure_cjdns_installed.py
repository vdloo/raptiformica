from raptiformica.shell.cjdns import ensure_cjdns_installed, CJDNS_REPOSITORY
from tests.testcase import TestCase


class TestEnsureCjdnsInstalled(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.cjdns.log')
        self.ensure_latest_source = self.set_up_patch('raptiformica.shell.cjdns.ensure_latest_source')
        self.ensure_cjdns_dependencies = self.set_up_patch('raptiformica.shell.cjdns.ensure_cjdns_dependencies')
        self.cjdns_setup = self.set_up_patch('raptiformica.shell.cjdns.cjdns_setup')

    def test_ensure_cjdns_installed_logs_installing_cjdns_message(self):
        ensure_cjdns_installed(host='1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_ensure_cjdns_installed_ensures_latest_source(self):
        ensure_cjdns_installed(host='1.2.3.4', port=2222)

        self.ensure_latest_source.assert_called_once_with(
            CJDNS_REPOSITORY,
            "cjdns",
            host='1.2.3.4',
            port=2222
        )

    def test_ensure_cjdns_installed_ensures_cjdns_dependencies(self):
        ensure_cjdns_installed(host='1.2.3.4', port=2222)

        self.ensure_cjdns_dependencies.assert_called_once_with(
            host='1.2.3.4',
            port=2222
        )

    def test_ensure_cjdns_installed_sets_up_cjdns(self):
        ensure_cjdns_installed(host='1.2.3.4', port=2222)

        self.cjdns_setup.assert_called_once_with(
            host='1.2.3.4', port=2222
        )

