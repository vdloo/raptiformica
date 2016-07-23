from raptiformica.shell.compute import create_new_compute_type_directory
from tests.testcase import TestCase


class TestCreateNewComputeTypeDirectory(TestCase):
    def setUp(self):
        self.ensure_compute_type_machines_directory_exists = self.set_up_patch(
            'raptiformica.shell.compute.ensure_compute_type_machines_directory_exists'
        )
        self.clone_source_locally = self.set_up_patch(
            'raptiformica.shell.compute.clone_source_locally'
        )
        self.path = self.set_up_patch('raptiformica.shell.compute.path')
        self.uuid4 = self.set_up_patch('raptiformica.shell.compute.uuid4')

    def test_create_new_compute_type_directory_ensure_compute_type_machines_directory_exists(self):
        create_new_compute_type_directory('vagrant', "https://github.com/vdloo/vagrantfiles")

        self.ensure_compute_type_machines_directory_exists.assert_called_once_with('vagrant')

    def test_create_new_compute_type_directory_joins_a_random_uuid_hex_to_the_compute_directory(self):
        create_new_compute_type_directory('vagrant', "https://github.com/vdloo/vagrantfiles")

        self.path.join.assert_called_once_with(
            self.ensure_compute_type_machines_directory_exists.return_value,
            self.uuid4.return_value.hex
        )

    def test_create_new_compute_type_directory_clones_source_locally(self):
        create_new_compute_type_directory('vagrant', "https://github.com/vdloo/vagrantfiles")

        self.clone_source_locally.assert_called_once_with(
            'https://github.com/vdloo/vagrantfiles',
            self.path.join.return_value
        )

    def test_create_new_compute_type_directory_returns_new_compute_checkout(self):
        ret = create_new_compute_type_directory('vagrant', "https://github.com/vdloo/vagrantfiles")

        self.assertEqual(ret, self.path.join.return_value)

