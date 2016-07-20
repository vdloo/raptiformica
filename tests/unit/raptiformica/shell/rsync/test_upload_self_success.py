from raptiformica.shell.rsync import upload_self_success
from tests.testcase import TestCase


class TestUploadSelfSuccess(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.rsync.log')
        self.process_output = (0, 'standard out output', None)

    def test_upload_self_logs_success_message(self):
        upload_self_success(self.process_output)

        self.assertTrue(self.log.info.called)
