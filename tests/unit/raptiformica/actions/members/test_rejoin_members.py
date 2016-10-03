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
        self.join_meshnet = self.set_up_patch(
            'raptiformica.actions.members.join_meshnet'
        )

    def test_rejoin_members_joins_meshnet(self):
        rejoin_members()

        self.join_meshnet.assert_called_once_with()