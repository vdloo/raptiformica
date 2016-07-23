from mock import call

from raptiformica.settings import MACHINES_DIR, EPHEMERAL_DIR
from raptiformica.shell.compute import ensure_compute_type_machines_directory_exists
from tests.testcase import TestCase


class TestEnsureComputeTypeMachinesDirectoryExists(TestCase):
    def setUp(self):
        self.path = self.set_up_patch('raptiformica.shell.compute.path')
        self.ensure_directory = self.set_up_patch('raptiformica.shell.compute.ensure_directory')

    def test_ensure_compute_type_machines_directory_exists_joins_machines_dir_to_compute_type(self):
        ensure_compute_type_machines_directory_exists('vagrant')

        self.path.join.assert_called_once_with(MACHINES_DIR, 'vagrant')

    def test_ensure_compute_type_machines_directory_ensures_all_directories(self):
        ensure_compute_type_machines_directory_exists('vagrant')

        expected_calls = map(call, (EPHEMERAL_DIR, MACHINES_DIR, self.path.join.return_value))
        self.assertCountEqual(expected_calls, self.ensure_directory.mock_calls)

    def test_ensure_compute_type_machines_directory_returns_compute_type_directory(self):
        ret = ensure_compute_type_machines_directory_exists('vagrant')

        self.assertEqual(ret, self.path.join.return_value)
