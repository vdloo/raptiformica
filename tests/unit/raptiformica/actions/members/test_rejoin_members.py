from raptiformica.actions.members import rejoin_members
from tests.testcase import TestCase


class TestRejoinMembers(TestCase):
    def setUp(self):
        self.configure_cjdroute_conf = self.set_up_patch(
            'raptiformica.actions.members.configure_cjdroute_conf'
        )
        self.configure_consul_conf = self.set_up_patch(
            'raptiformica.actions.members.configure_consul_conf'
        )
        self.ensure_cjdns_routing = self.set_up_patch(
            'raptiformica.actions.members.ensure_cjdns_routing'
        )
        self.join_meshnet = self.set_up_patch(
            'raptiformica.actions.members.join_meshnet'
        )

    def test_rejoin_members_configures_cjdroute_conf(self):
        rejoin_members()

        self.configure_cjdroute_conf.assert_called_once_with()

    def test_rejoin_members_configures_consul_conf(self):
        rejoin_members()

        self.configure_consul_conf.assert_called_once_with()

    def test_rejoin_members_ensures_cjdns_routing(self):
        rejoin_members()

        self.ensure_cjdns_routing.assert_called_once_with()

    def test_rejoin_members_joins_meshnet(self):
        rejoin_members()

        self.join_meshnet.assert_called_once_with()