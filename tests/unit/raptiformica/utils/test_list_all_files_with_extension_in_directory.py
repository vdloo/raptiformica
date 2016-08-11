from raptiformica.utils import list_all_files_with_extension_in_directory
from tests.testcase import TestCase


class TestListAllFilesWithExtensionInDirectory(TestCase):
    def setUp(self):
        self.list_all_files_in_directory = self.set_up_patch('raptiformica.utils.list_all_files_in_directory')
        self.list_all_files_in_directory.return_value = (
            '/tmp/a/directory/config2.json',
            '/tmp/a/directory/file.txt',
            '/tmp/a/directory/dir2/config1.json',
            '/tmp/a/directory/dir/file2.txt'
        )

    def test_list_all_files_with_extension_in_directory_lists_all_files_with_extension_in_directory(self):
        list_all_files_with_extension_in_directory('/tmp/a/directory', 'json')

        self.list_all_files_in_directory.assert_called_once_with('/tmp/a/directory')

    def test_list_all_files_with_extension_in_directory_returns_only_files_with_specified_extension(self):
        ret1 = list_all_files_with_extension_in_directory('/tmp/a/directory', 'json')
        ret2 = list_all_files_with_extension_in_directory('/tmp/a/directory', 'txt')

        expected_list1 = (
            '/tmp/a/directory/config2.json',
            '/tmp/a/directory/dir2/config1.json'
        )
        expected_list2 = (
            '/tmp/a/directory/file.txt',
            '/tmp/a/directory/dir/file2.txt'
        )
        self.assertCountEqual(ret1, expected_list1)
        self.assertCountEqual(ret2, expected_list2)

