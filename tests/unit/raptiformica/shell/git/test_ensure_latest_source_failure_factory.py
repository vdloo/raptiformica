from raptiformica.shell.git import ensure_latest_source_failure_factory
from tests.testcase import TestCase


class TestEnsureLatestSourceFailureFactory(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.git.log')
        self.clone_source_remotely = self.set_up_patch('raptiformica.shell.git.clone_source_remotely')
        self.process_output = (1, 'standard out output', 'standard error output')

    def test_that_ensure_latest_source_failure_factory_returns_function_that_logs_failure_message(self):
        func = ensure_latest_source_failure_factory(
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles',
            '1.2.3.4',
            port=22
        )
        func(self.process_output)

        self.assertTrue(self.log.info)

    def test_that_ensure_latest_source_failure_factory_returns_function_that_clones_source(self):
        func = ensure_latest_source_failure_factory(
                'https://github.com/vdloo/puppetfiles',
                '/usr/etc/puppetfiles',
                '1.2.3.4',
                port=22
        )
        func(self.process_output)

        self.clone_source_remotely.assert_called_once_with(
            'https://github.com/vdloo/puppetfiles',
            '/usr/etc/puppetfiles',
            '1.2.3.4',
            port=22
        )

