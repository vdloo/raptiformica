from raptiformica.shell.git import pull_origin_master_failure
from tests.testcase import TestCase


class TestPullOriginMasterFailure(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.git.log')
        self.process_output = (1, 'standard out output', 'standard error output')

    def test_that_pull_origin_master_failure_logs_failure_warning(self):
        pull_origin_master_failure(self.process_output)

        self.assertTrue(self.log.warning.called)
