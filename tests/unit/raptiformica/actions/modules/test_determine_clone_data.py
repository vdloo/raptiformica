from raptiformica.actions.modules import determine_clone_data
from tests.testcase import TestCase


class TestDetermineCloneData(TestCase):
    def test_determine_clone_data_returns_github_url_module_name_pair(self):
        url, name = determine_clone_data('vdloo/puppetfiles')

        self.assertEqual(
            url,
            'https://github.com/vdloo/puppetfiles'
        )
        self.assertEqual(
            name,
            'puppetfiles'
        )

    def test_determine_clone_data(self):
        url, name = determine_clone_data('https://example.com/puppetfiles.git')

        self.assertEqual(
            url,
            'https://example.com/puppetfiles.git'
        )
        self.assertEqual(
            name,
            'puppetfiles'
        )
