from raptiformica.cli import advertise
from tests.testcase import TestCase


class TestAdvertise(TestCase):
    def setUp(self):
        self.parse_advertise_arguments = self.set_up_patch(
            'raptiformica.cli.parse_advertise_arguments'
        )
        self.write_last_advertised = self.set_up_patch(
            'raptiformica.cli.write_last_advertised'
        )

    def test_advertise_parses_advertise_arguments(self):
        advertise()

        self.parse_advertise_arguments.assert_called_once_with()

    def test_advertise_writes_last_advertised(self):
        advertise()

        self.write_last_advertised.assert_called_once_with(
            self.parse_advertise_arguments.return_value.host,
            self.parse_advertise_arguments.return_value.port
        )
