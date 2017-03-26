from consul_kv.api import put_kv, get_kv, delete_kv, put_kv_txn
from consul_kv.serializer import map_dictionary, dictionary_map
from consul_kv.settings import DEFAULT_KV_ENDPOINT, DEFAULT_REQUEST_TIMEOUT


class Connection(object):
    """
    Client for the consul key value store API
    """
    kv_endpoint = DEFAULT_KV_ENDPOINT
    timeout = DEFAULT_REQUEST_TIMEOUT

    @staticmethod
    def _kv_endpoint_to_txn_endpoint(kv_endpoint):
        """
        Rewrite a key/value endpoint to a txn endpoint for atomic updates
        :param str kv_endpoint: endpoint to replace the kv path for with txn
        :return str txn_endpoint: the url with the kv path replaced with txn
        """
        return kv_endpoint.replace('/v1/kv', '/v1/txn')

    def __init__(self, endpoint=None, timeout=None):
        self.kv_endpoint = endpoint or self.kv_endpoint
        self.txn_endpoint = self._kv_endpoint_to_txn_endpoint(
            self.kv_endpoint
        )
        self.timeout = timeout or DEFAULT_REQUEST_TIMEOUT

    def put(self, k, v):
        """
        Put a key value pair at the configured endpoint
        :param str k: key to put
        :param str v: value to put
        :return None:
        """
        return put_kv(k, v, endpoint=self.kv_endpoint, timeout=self.timeout)

    def put_mapping(self, mapping):
        """
        Atomically (Txn) put a key/value mapping at the configured endpoint
        :param dict mapping: dict of key/values put
        :return None:
        """
        return put_kv_txn(
            mapping, endpoint=self.txn_endpoint, timeout=self.timeout
        )

    def put_dict(self, dictionary):
        """
        Atomically (Txn) put a dict at the configured endpoint
        :param dict dictionary: dict of nested keys and values
        {'some': {'key1': 'value1', 'key2': 'value2'} ->
        [{'some/key1': 'value1, 'some/key2': 'value2}]
        :return None:
        """
        mapping = map_dictionary(dictionary)
        return self.put_mapping(mapping)

    def get(self, k=None, recurse=False):
        """
        Get a value for a key or all values under that key if recursive is specified
        :param str k: key to get
        :param bool recurse: return nested entries
        :return dict mapping: retrieved key/value mapping
        """
        return get_kv(
            k=k, recurse=recurse, endpoint=self.kv_endpoint,
            timeout=self.timeout
        )

    def get_mapping(self, k=None):
        """
        Retrieve a key value mapping from a specified key
        Note: contrary to put_mapping, this method is not atomic
        :param k: The key to get recursively and return as a key value mapping
        :return dict mapping: The retrieved key value mapping
        """
        return self.get(k=k, recurse=True)

    def get_dict(self, k=None):
        """
        Retrieve a dict that represents nested key value entries from the specified
        endpoint. [{'some/key1': 'value1, 'some/key2': 'value2}] ->
        {'some': {'key1': 'value1', 'key2': 'value2'}
        Note: contrary to put_dict, this method is not atomic
        :param k: The key to get recursively and return as a dict
        :return dict dictionary: The retrieved dict of nested keys and values
        """
        mapping = self.get_mapping(k=k)
        return dictionary_map(mapping)

    def delete(self, k=None, recurse=False):
        """
        Delete the specified key or all values under that key if recursive is specified
        :param str k: key to delete
        :param bool recurse: delete nested entries
        :return None:
        """
        return delete_kv(
            k=k, recurse=recurse,
            endpoint=self.kv_endpoint, timeout=self.timeout
        )
