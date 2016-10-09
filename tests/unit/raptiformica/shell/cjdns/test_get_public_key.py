from raptiformica.shell.cjdns import get_public_key
from tests.testcase import TestCase


class TestGetPublicKey(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.cjdns.log')
        self.get_cjdns_config_item = self.set_up_patch(
            'raptiformica.shell.cjdns.get_cjdns_config_item'
        )

    def test_get_public_key_logs_gettings_public_key_message(self):
        get_public_key(host='1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_get_public_key_gets_public_key(self):
        get_public_key(host='1.2.3.4', port=2222)

        self.get_cjdns_config_item.assert_called_once_with(
            'publicKey', host='1.2.3.4', port=2222
        )

    def test_get_public_key_returns_public_key(self):
        ret = get_public_key(host='1.2.3.4', port=2222)

        self.assertEqual(ret, self.get_cjdns_config_item.return_value)
