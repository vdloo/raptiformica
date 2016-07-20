from raptiformica.shell.git import ensure_latest_source_success_factory

from tests.testcase import TestCase


class TestEnsureLatestSourceSuccessFactory(TestCase):
    def setUp(self):
        self.update_source = self.set_up_patch('raptiformica.shell.git.update_source')
        self.log = self.set_up_patch('raptiformica.shell.git.log')
        self.process_output = (0, 'standard out output', None)

    def test_that_ensure_latest_source_success_factory_returns_function_that_logs_success_message(self):
        func = ensure_latest_source_success_factory('/usr/etc/puppetfiles', '1.2.3.4', port=22)
        func(self.process_output)

        self.assertTrue(self.log.info.called)

    def test_that_ensure_latest_source_success_factory_returns_function_that_updates_source(self):
        func = ensure_latest_source_success_factory('/usr/etc/puppetfiles', '1.2.3.4', port=22)
        func(self.process_output)

        self.update_source.assert_called_once_with('/usr/etc/puppetfiles', '1.2.3.4', port=22)
