from raptiformica.utils import file_age_in_seconds
from tests.testcase import TestCase


class TestFileAgeInSeconds(TestCase):
    def setUp(self):
        self.time = self.set_up_patch(
            'raptiformica.utils.time'
        )
        self.time.return_value = 12345
        self.getmtime = self.set_up_patch(
            'raptiformica.utils.getmtime'
        )
        self.getmtime.return_value = 12121

    def test_file_age_in_seconds_gets_current_time(self):
        file_age_in_seconds('/some/file')

        self.time.assert_called_once_with()

    def test_file_age_in_seconds_gets_mtime_of_file(self):
        file_age_in_seconds('/some/file')

        self.getmtime.assert_called_once_with(
            '/some/file'
        )

    def test_file_age_in_seconds_returns_difference_between_current_time_and_mtime(self):
        ret = file_age_in_seconds('/some/file')

        expected_time = self.time.return_value - self.getmtime.return_value
        self.assertEqual(
            ret, expected_time
        )
