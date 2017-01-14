from raptiformica.cli import package
from tests.testcase import TestCase


class TestPackage(TestCase):
    def setUp(self):
        self.parse_package_arguments = self.set_up_patch(
            'raptiformica.cli.parse_package_arguments'
        )
        self.args = self.parse_package_arguments.return_value
        # patching the original function instead of the function in the scope
        # of cli.py because this is a conditional import and so that function
        # won't be available to patch until the function that imports it is
        # evaluated.
        self.package_machine = self.set_up_patch(
            'raptiformica.actions.package.package_machine'
        )

    def test_package_parses_package_arguments(self):
        package()

        self.parse_package_arguments.assert_called_once_with()

    def test_package_packages_machine(self):
        package()

        self.package_machine.assert_called_once_with(
            server_type=self.args.server_type,
            compute_type=self.args.compute_type,
            only_check_available=self.args.check_available
        )
