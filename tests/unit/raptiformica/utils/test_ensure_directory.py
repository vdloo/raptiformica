from raptiformica.utils import ensure_directory
from tests.testcase import TestCase


class TestEnsureDirectory(TestCase):
    def setUp(self):
        self.makedirs = self.set_up_patch('raptiformica.utils.makedirs')

    def test_ensure_directory_makes_dirs_if_path_does_not_exist(self):
        ensure_directory('/tmp/directory')

        self.makedirs.assert_called_once_with('/tmp/directory')

    def test_ensure_directory_does_not_raise_exception_if_dir_already_exists(self):
        self.makedirs.side_effect = FileExistsError

        ensure_directory('/tmp/directory')
