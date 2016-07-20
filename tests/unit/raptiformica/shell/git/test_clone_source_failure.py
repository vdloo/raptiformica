from raptiformica.shell.git import clone_source_failure
from tests.testcase import TestCase


class TestCloneSourceFailure(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.git.log')
        self.process_output = (1, 'standard out output', 'standard error output')

    def test_that_clone_source_failure_logs_failure_warning(self):
        clone_source_failure(self.process_output)

        self.assertTrue(self.log.warning.called)
