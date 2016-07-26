from raptiformica.actions.slave import assimilate_machine
from tests.testcase import TestCase


class TestAssimilateMachine(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.slave.log')
        self.ensure_cjdns_installed = self.set_up_patch('raptiformica.actions.slave.ensure_cjdns_installed')

    def test_assimilate_machine_logs_assimilating_machine_message(self):
        assimilate_machine('1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_assimilate_machine_ensures_cjdns_is_installed(self):
        assimilate_machine('1.2.3.4', port=2222)

        self.ensure_cjdns_installed.assert_called_once_with('1.2.3.4', port=2222)

