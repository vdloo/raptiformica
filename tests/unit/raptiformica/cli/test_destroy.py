from raptiformica.cli import destroy
from tests.testcase import TestCase


class TestDestroy(TestCase):
    def setUp(self):
        self.parse_destroy_arguments = self.set_up_patch('raptiformica.cli.parse_destroy_arguments')
        self.args = self.parse_destroy_arguments.return_value
        self.destroy_cluster = self.set_up_patch('raptiformica.cli.destroy_cluster')

    def test_destroy_parses_destroy_arguments(self):
        destroy()

        self.parse_destroy_arguments.assert_called_once_with()

    def test_destroy_destroys_cluster(self):
        destroy()

        self.destroy_cluster.assert_called_once_with(
            purge_artifacts=self.args.purge_artifacts,
            purge_modules=self.args.purge_modules,
        )
