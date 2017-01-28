from raptiformica.shell.consul import ensure_consul_installed
from tests.testcase import TestCase


class TestEnsureConsulInstalled(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.consul.log')
        self.ensure_latest_consul_release = self.set_up_patch('raptiformica.shell.consul.ensure_latest_consul_release')
        self.ensure_consul_dependencies = self.set_up_patch('raptiformica.shell.consul.ensure_consul_dependencies')
        self.unzip_consul_release = self.set_up_patch('raptiformica.shell.consul.unzip_consul_release')

    def test_ensure_consul_installed_ensure_latest_consul_release(self):
        ensure_consul_installed(host='1.2.3.4', port=2222)

        self.ensure_latest_consul_release.assert_called_once_with(
            host='1.2.3.4', port=2222
        )

    def test_ensure_consul_installed_ensures_consul_dependencies(self):
        ensure_consul_installed(host='1.2.3.4', port=2222)

        self.ensure_consul_dependencies.assert_called_once_with(
            host='1.2.3.4', port=2222
        )

    def test_ensure_consul_installed_unzips_consul_release(self):
        ensure_consul_installed(host='1.2.3.4', port=2222)

        self.unzip_consul_release.assert_called_once_with(
            host='1.2.3.4', port=2222
        )

