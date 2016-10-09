from raptiformica.shell.consul import unzip_consul_release
from tests.testcase import TestCase


class TestUnzipConsulRelease(TestCase):
    def setUp(self):
        self.unzip_consul_binary = self.set_up_patch(
            'raptiformica.shell.consul.unzip_consul_binary'
        )
        self.unzip_consul_web_ui = self.set_up_patch(
            'raptiformica.shell.consul.unzip_consul_web_ui'
        )

    def test_unzip_consul_release_unzips_consul_binary_on_remote_host(self):
        unzip_consul_release(host='1.2.3.4', port=22)

        self.unzip_consul_binary.assert_called_once_with(
            host='1.2.3.4', port=22
        )

    def test_unzip_consul_release_unzips_consul_web_ui_on_remote_host(self):
        unzip_consul_release(host='1.2.3.4', port=22)

        self.unzip_consul_web_ui.assert_called_once_with(
            host='1.2.3.4', port=22
        )
