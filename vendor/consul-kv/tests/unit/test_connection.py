from consul_kv import Connection, DEFAULT_KV_ENDPOINT, DEFAULT_REQUEST_TIMEOUT
from consul_kv.api import DEFAULT_KV_ENDPOINT
from tests.testcase import TestCase


class TestConnection(TestCase):
    def setUp(self):
        self.put_kv = self.set_up_patch('consul_kv.put_kv')
        self.put_kv_txn = self.set_up_patch('consul_kv.put_kv_txn')
        self.get_kv = self.set_up_patch('consul_kv.get_kv')
        self.get_kv_meta = self.set_up_patch('consul_kv.get_kv_meta')
        self.get_kv_cas = self.set_up_patch('consul_kv.get_kv_cas')
        self.delete_kv = self.set_up_patch('consul_kv.delete_kv')
        self.kv_endpoint = 'http://some_host:8500/v1/kv/'
        self.txn_endpoint = 'http://some_host:8500/v1/txn/'
        self.conn = Connection(endpoint=self.kv_endpoint, timeout=10)
        self.mapping = {
            'some/key/1': 'some_value_1',
            'some/key/2': 'some_value_2'
        }
        self.dictionary = {
            'some': {'key': {'1': 'some_value1', '2': 'some_value2'}}
        }
        self.map_dictionary = self.set_up_patch('consul_kv.map_dictionary')

    def test_connection_has_correct_kv_endpoint(self):
        self.assertEqual(self.conn.kv_endpoint, self.kv_endpoint)

    def test_connection_has_specified_request_timeout(self):
        self.assertEqual(self.conn.timeout, 10)

    def test_connection_uses_default_kv_endpoint_if_none_specified(self):
        conn = Connection()

        self.assertEqual(conn.kv_endpoint, DEFAULT_KV_ENDPOINT)

    def test_connection_uses_default_request_timeout_if_none_specified(self):
        conn = Connection()

        self.assertEqual(conn.timeout, DEFAULT_REQUEST_TIMEOUT)

    def test_connection_put_calls_put_kv_with_kv_endpoint(self):
        self.conn.put('key1', 'value1')

        self.put_kv.assert_called_once_with(
            'key1', 'value1', None, endpoint=self.kv_endpoint,
            timeout=10
        )

    def test_connection_put_calls_put_kv_with_specified_cas_version(self):
        self.conn.put('key1', 'value1', cas=123)

        self.put_kv.assert_called_once_with(
            'key1', 'value1', 123, endpoint=self.kv_endpoint,
            timeout=10
        )

    def test_connection_put_mapping_calls_put_kv_txn_with_txn_endpoint(self):
        self.conn.put_mapping(self.mapping)

        self.put_kv_txn.assert_called_once_with(
            self.mapping, endpoint=self.txn_endpoint,
            timeout=10
        )

    def test_connection_put_dict_maps_dictionary(self):
        self.conn.put_dict(self.dictionary)

        self.map_dictionary.assert_called_once_with(self.dictionary)

    def test_connection_put_dict_puts_mapping(self):
        put_mapping = self.set_up_patch('consul_kv.Connection.put_mapping')

        self.conn.put_dict(self.dictionary)

        put_mapping.assert_called_once_with(self.map_dictionary.return_value)

    def test_connection_get_calls_get_kv_with_kv_endpoint(self):
        self.conn.get('key1')

        self.get_kv.assert_called_once_with(
            k='key1', recurse=False, endpoint=self.kv_endpoint,
            timeout=10
        )

    def test_connection_get_recurses_if_specified(self):
        self.conn.get('key2', recurse=True)

        self.get_kv.assert_called_once_with(
            k='key2', recurse=True, endpoint=self.kv_endpoint,
            timeout=10
        )

    def test_connection_get_returns_api_result(self):
        ret = self.conn.get('key2', recurse=True)

        self.assertEqual(ret, self.get_kv.return_value)

    def test_connection_get_cas_calls_get_kv_cas_with_kv_endpoint(self):
        self.conn.get_cas('key1')

        self.get_kv_cas.assert_called_once_with(
            k='key1', recurse=False, endpoint=self.kv_endpoint,
            timeout=10
        )

    def test_connection_get_cas_recurses_if_specified(self):
        self.conn.get_cas('key1', recurse=True)

        self.get_kv_cas.assert_called_once_with(
            k='key1', recurse=True, endpoint=self.kv_endpoint,
            timeout=10
        )

    def test_connection_get_cas_returns_api_result(self):
        ret = self.conn.get_cas('key2')

        self.assertEqual(ret, self.get_kv_cas.return_value)

    def test_connection_get_meta_calls_get_kv_meta_with_kv_endpoint(self):
        self.conn.get_meta('key1')

        self.get_kv_meta.assert_called_once_with(
            k='key1', recurse=False, endpoint=self.kv_endpoint,
            timeout=10
        )

    def test_connection_get_meta_recurses_if_specified(self):
        self.conn.get_meta('key1', recurse=True)

        self.get_kv_meta.assert_called_once_with(
            k='key1', recurse=True, endpoint=self.kv_endpoint,
            timeout=10
        )

    def test_connection_get_meta_returns_api_result(self):
        ret = self.conn.get_meta('key2')

        self.assertEqual(ret, self.get_kv_meta.return_value)

    def test_connection_get_mapping_calls_get_recursively(self):
        get = self.set_up_patch('consul_kv.Connection.get')

        self.conn.get_mapping('key1')

        get.assert_called_once_with(k='key1', recurse=True)

    def test_connection_get_mapping_returns_mapping(self):
        get = self.set_up_patch('consul_kv.Connection.get')

        ret = self.conn.get_mapping('key1')

        self.assertEqual(ret, get.return_value)

    def test_connection_get_dict_calls_get_mapping(self):
        get_mapping = self.set_up_patch('consul_kv.Connection.get_mapping')
        self.set_up_patch('consul_kv.dictionary_map')

        self.conn.get_dict('key2')

        get_mapping.assert_called_once_with(k='key2')

    def test_connection_get_dict_converts_key_value_mapping_into_dictionary(self):
        get_mapping = self.set_up_patch('consul_kv.Connection.get_mapping')
        dictionary_map = self.set_up_patch('consul_kv.dictionary_map')

        self.conn.get_dict('key2')

        dictionary_map.assert_called_once_with(get_mapping.return_value)

    def test_connection_get_dict_returns_converted_mapping(self):
        self.set_up_patch('consul_kv.Connection.get_mapping')
        dictionary_map = self.set_up_patch('consul_kv.dictionary_map')

        ret = self.conn.get_dict('key2')

        self.assertEqual(ret, dictionary_map.return_value)

    def test_connection_delete_calls_delete_kv_with_kv_endpoint(self):
        self.conn.delete('key1')

        self.delete_kv.assert_called_once_with(
            k='key1', recurse=False, endpoint=self.kv_endpoint,
            timeout=10
        )

    def test_connection_delete_recurses_if_specified(self):
        self.conn.delete('key2', recurse=True)

        self.delete_kv.assert_called_once_with(
            k='key2', recurse=True, endpoint=self.kv_endpoint,
            timeout=10
        )
