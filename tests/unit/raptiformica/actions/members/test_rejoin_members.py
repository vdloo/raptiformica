from raptiformica.actions.members import rejoin_members
from tests.testcase import TestCase


class TestRejoinMembers(TestCase):
    def setUp(self):
        self.join_meshnet = self.set_up_patch(
            'raptiformica.actions.members.join_meshnet'
        )

    def test_rejoin_members_joins_meshnet(self):
        rejoin_members()

        self.join_meshnet.assert_called_once_with()