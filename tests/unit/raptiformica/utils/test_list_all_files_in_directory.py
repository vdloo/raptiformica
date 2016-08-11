from raptiformica.utils import list_all_files_in_directory
from tests.testcase import TestCase


class TestListAllFilesInDirectory(TestCase):
    def setUp(self):
        self.walk = self.set_up_patch('raptiformica.utils.walk')
        self.walk.return_value = [
            ('/tmp/a/directory', ['dir'], ['file.txt', 'file2.txt']),
            ('/tmp/a/directory/dir', ['dir2'], ['file3.txt']),
            ('/tmp/a/directory/dir/dir2', [], ['file5.txt', 'file4.txt'])
        ]

    def test_list_all_files_in_directory_lists_all_files_in_directory_walks_path(self):
        list_all_files_in_directory('/tmp/a/directory')

        self.walk.assert_called_once_with('/tmp/a/directory')

    def test_list_all_files_in_directory_returns_all_files(self):
        ret = list_all_files_in_directory('/tmp/a/directory')

        expected_list = [
            '/tmp/a/directory/file.txt',
            '/tmp/a/directory/file2.txt',
            '/tmp/a/directory/dir/file3.txt',
            '/tmp/a/directory/dir/dir2/file4.txt',
            '/tmp/a/directory/dir/dir2/file5.txt'
        ]
        self.assertCountEqual(ret, expected_list)
