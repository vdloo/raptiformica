from tempfile import NamedTemporaryFile

from raptiformica.utils import calculate_checksum
from tests.testcase import TestCase


class TestCalculateChecksum(TestCase):
    def test_calculate_checksum_creates_the_same_hash_of_the_same_file_twice(self):
        with NamedTemporaryFile() as f:
            f.write(b"some_content")
            f.flush()
            checksum_1 = calculate_checksum(f.name)
            checksum_2 = calculate_checksum(f.name)

        self.assertEqual(checksum_1, checksum_2)

    def test_calculate_checksum_creates_a_different_checksum_for_a_file_with_different_content(self):
        with NamedTemporaryFile() as f:
            f.write(b"some_content")
            f.flush()
            checksum_1 = calculate_checksum(f.name)
        with NamedTemporaryFile() as f:
            f.write(b"some_other_content")
            f.flush()
            checksum_2 = calculate_checksum(f.name)

        self.assertNotEqual(checksum_1, checksum_2)

    def test_calculate_checksum_creates_the_same_hash_for_two_files_with_the_same_content(self):
        with NamedTemporaryFile() as f:
            f.write(b"some_content")
            f.flush()
            checksum_1 = calculate_checksum(f.name)
        with NamedTemporaryFile() as f:
            f.write(b"some_content")
            f.flush()
            checksum_2 = calculate_checksum(f.name)

        self.assertEqual(checksum_1, checksum_2)
