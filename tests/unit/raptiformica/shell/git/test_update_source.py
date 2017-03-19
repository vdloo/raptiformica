from raptiformica.shell.git import update_source
from tests.testcase import TestCase


class TestUpdateSource(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.git.log')
        self.pull_origin_master = self.set_up_patch('raptiformica.shell.git.pull_origin_master')
        self.pull_origin_master.return_value = 0
        self.reset_hard_origin_master = self.set_up_patch('raptiformica.shell.git.reset_hard_head')

    def test_that_update_source_logs_updating_source_message(self):
        update_source('/usr/etc/puppetfiles', '1.2.3.4', port=22)

        self.assertTrue(self.log.info.called)

    def test_that_update_source_pulls_origin_master(self):
        update_source('/usr/etc/puppetfiles', '1.2.3.4', port=22)

        self.pull_origin_master.assert_called_once_with(
            '/usr/etc/puppetfiles',
            host='1.2.3.4',
            port=22
        )

    def test_that_update_source_resets_to_head_if_pulling_origin_master_returned_nonzero(self):
        self.pull_origin_master.return_value = 1

        update_source('/usr/etc/puppetfiles', '1.2.3.4', port=22)

        self.reset_hard_origin_master.assert_called_once_with(
            '/usr/etc/puppetfiles',
            host='1.2.3.4',
            port=22
        )

    def test_that_update_source_does_not_reset_to_head_if_pulling_origin_master_returned_zero(self):
        update_source('/usr/etc/puppetfiles', '1.2.3.4', port=22)

        self.assertFalse(self.reset_hard_origin_master.called)
