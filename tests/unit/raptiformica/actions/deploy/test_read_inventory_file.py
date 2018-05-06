from tempfile import NamedTemporaryFile

from raptiformica.actions.deploy import read_inventory_file
from raptiformica.utils import write_json
from tests.testcase import TestCase


class TestReadInventoryFile(TestCase):
    def test_read_inventory_file_returns_inventory_hosts(self):
        in_data = [
            {'dst': '1.2.3.4'},
            {'dst': '1.2.3.5', 'via': '1.2.3.4'},
            {'dst': '2.3.4.1', 'port': 2222}
        ]
        with NamedTemporaryFile() as f:
            write_json(in_data, f.name)
            f.flush()

            out_data = read_inventory_file(f.name)

        self.assertListEqual(out_data, in_data)

    def test_read_inventory_file_raise_value_error_if_missing_dst(self):
        in_data = [
            {'bla': '1.2.3.4'},
            {'dst': '1.2.3.5', 'via': '1.2.3.4'},
            {'dst': '2.3.4.1', 'port': 2222}
        ]
        with NamedTemporaryFile() as f:
            write_json(in_data, f.name)
            f.flush()

            with self.assertRaises(ValueError):
                read_inventory_file(f.name)

    def test_read_inventory_file_raise_value_error_if_missing_via(self):
        in_data = [
            {'dst': '1.2.3.4'},
            {'dst': '1.2.3.5', 'via': '1.2.3.2'},
            {'dst': '2.3.4.1', 'port': 2222}
        ]
        with NamedTemporaryFile() as f:
            write_json(in_data, f.name)
            f.flush()

            with self.assertRaises(ValueError):
                read_inventory_file(f.name)

    def test_read_inventory_file_raise_value_error_if_via_is_dst(self):
        in_data = [
            {'dst': '1.2.3.5'},
            {'dst': '1.2.3.5', 'via': '1.2.3.5'},
            {'dst': '2.3.4.1', 'port': 2222}
        ]
        with NamedTemporaryFile() as f:
            write_json(in_data, f.name)
            f.flush()

            with self.assertRaises(ValueError):
                read_inventory_file(f.name)
