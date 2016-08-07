from os.path import join

from raptiformica.actions.prune import list_compute_checkouts_for_server_type_of_compute_type
from raptiformica.settings import EPHEMERAL_DIR
from raptiformica.settings import MACHINES_DIR
from tests.testcase import TestCase


class TestListComputeCheckoutsForServerTypeOfComputeType(TestCase):
    def setUp(self):
        self.isdir = self.set_up_patch('raptiformica.actions.prune.isdir')
        self.isdir.return_value = True
        self.listdir = self.set_up_patch('raptiformica.actions.prune.listdir')
        self.listdir.return_value = ['a_generated_uuid1', 'a_generated_uuid2']

    def test_list_compute_checkouts_for_server_type_of_compute_type_lists_compute_checkouts(self):
        ret = list_compute_checkouts_for_server_type_of_compute_type(
            'headless', 'docker'
        )

        directories = EPHEMERAL_DIR, MACHINES_DIR, 'docker', 'headless'
        server_type_of_compute_type_directory = join(*directories)
        expected_compute_checkouts = [
            ('headless', 'docker',
             server_type_of_compute_type_directory + '/a_generated_uuid1'),
            ('headless', 'docker',
             server_type_of_compute_type_directory + '/a_generated_uuid2'),
        ]
        self.assertCountEqual(ret, expected_compute_checkouts)

    def test_list_compute_checkouts_for_server_type_of_compute_type_does_not_list_checkouts_if_no_such_dir(self):
        self.isdir.return_value = False

        ret = list_compute_checkouts_for_server_type_of_compute_type(
            'headless', 'docker'
        )

        self.assertFalse(self.listdir.called)
        expected_compute_checkouts = []
        self.assertCountEqual(ret, expected_compute_checkouts)
