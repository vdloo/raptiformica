from raptiformica.shell.rsync import upload_self_failure
from tests.testcase import TestCase


class TestUploadSelfFailure(TestCase):
    def setUp(self):
        self.process_output = (1, 'standard out output', 'standard error output')

    def test_upload_self_failure_raises_runtime_error(self):
        with self.assertRaises(RuntimeError):
            upload_self_failure(self.process_output)