from raptiformica.utils import ensure_directory
from tests.testcase import TestCase


class TestEnsureDirectory(TestCase):
    def setUp(self):
        self.path = self.set_up_patch('raptiformica.utils.path')
        self.path.exists.return_value = True
        self.makedirs = self.set_up_patch('raptiformica.utils.makedirs')

    def test_ensure_directory_checks_if_directory_already_exists(self):
        ensure_directory('/tmp/directory')

        self.path.exists.assert_called_once_with('/tmp/directory')

    def test_ensure_directory_makes_dirs_if_path_does_not_exist(self):
        self.path.exists.return_value = False

        ensure_directory('/tmp/directory')

        self.makedirs.assert_called_once_with('/tmp/directory')

    def test_ensure_directory_does_not_create_directory_if_it_already_exists(self):
        ensure_directory('/tmp/directory')

        self.assertFalse(self.makedirs.called)
