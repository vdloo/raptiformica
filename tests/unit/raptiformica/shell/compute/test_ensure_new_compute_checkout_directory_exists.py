from mock import call

from raptiformica.settings import MACHINES_DIR, EPHEMERAL_DIR
from raptiformica.shell.compute import ensure_new_compute_checkout_directory_exists
from tests.testcase import TestCase


class TestEnsureNewComputeCheckoutDirectoryExists(TestCase):
    def setUp(self):
        self.path = self.set_up_patch('raptiformica.shell.compute.path')
        self.ensure_directory = self.set_up_patch('raptiformica.shell.compute.ensure_directory')

    def test_ensure_compute_type_machines_directory_exists_joins_machines_dir_to_compute_type_and_server_type(self):
        ensure_new_compute_checkout_directory_exists('headless', 'vagrant')

        expected_calls = [
            call(MACHINES_DIR, 'vagrant'),
            call(self.path.join.return_value, 'headless')
        ]
        self.assertCountEqual(self.path.join.mock_calls, expected_calls)

    def test_ensure_compute_type_machines_directory_ensures_all_directories(self):
        ensure_new_compute_checkout_directory_exists('headless', 'vagrant')

        expected_calls = map(call, (EPHEMERAL_DIR, MACHINES_DIR,
                                    self.path.join.return_value,
                                    self.path.join.return_value))
        self.assertCountEqual(expected_calls, self.ensure_directory.mock_calls)

    def test_ensure_compute_type_machines_directory_returns_compute_type_directory(self):
        ret = ensure_new_compute_checkout_directory_exists('headless', 'vagrant')

        self.assertEqual(ret, self.path.join.return_value)
