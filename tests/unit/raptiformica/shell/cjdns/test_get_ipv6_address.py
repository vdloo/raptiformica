from raptiformica.shell.cjdns import get_ipv6_address
from tests.testcase import TestCase


class TestGetIpv6Address(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.cjdns.log')
        self.get_cjdns_config_item = self.set_up_patch('raptiformica.shell.cjdns.get_cjdns_config_item')

    def test_get_ipv6_address_logs_gettings_ipv6_address_message(self):
        get_ipv6_address(host='1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_get_ipv6_address_gets_ipv6_address(self):
        get_ipv6_address(host='1.2.3.4', port=2222)

        self.get_cjdns_config_item.assert_called_once_with(
            'ipv6', host='1.2.3.4', port=2222
        )

    def test_get_ipv6_address_returns_ipv6_address(self):
        ret = get_ipv6_address(host='1.2.3.4', port=2222)

        self.assertEqual(ret, self.get_cjdns_config_item.return_value)
