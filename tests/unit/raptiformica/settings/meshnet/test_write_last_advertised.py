from raptiformica.settings import conf
from raptiformica.settings.meshnet import write_last_advertised
from tests.testcase import TestCase


class TestWriteLastAdvertised(TestCase):
    def setUp(self):
        self.write_json = self.set_up_patch(
            'raptiformica.settings.meshnet.write_json'
        )

    def test_write_last_advertised_writes_last_advertised_json(self):
        write_last_advertised('1.2.3.4', 22)

        expected_last_advertised_data = {
            'host': '1.2.3.4', 'port': 22
        }
        self.write_json.assert_called_once_with(
            expected_last_advertised_data,
            conf().LAST_ADVERTISED
        )