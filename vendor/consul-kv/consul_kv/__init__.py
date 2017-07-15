from os.path import join
from consul_kv.api import put_kv, get_kv, get_kv_cas, get_kv_meta, delete_kv, put_kv_txn
from consul_kv.serializer import map_dictionary, dictionary_map
from consul_kv.settings import DEFAULT_ENDPOINT, DEFAULT_REQUEST_TIMEOUT


class Connection(object):
    """
    Client for the consul key value store API
    """
    endpoint = DEFAULT_ENDPOINT
    timeout = DEFAULT_REQUEST_TIMEOUT

    def __init__(self, endpoint=None, timeout=None):
        self.endpoint = endpoint or self.endpoint
        self.timeout = timeout or DEFAULT_REQUEST_TIMEOUT

    def put(self, k, v, cas=None):
        """
        Put a key value pair at the configured endpoint
        :param str k: key to put
        :param int cas: the cas version number. If None, no cas is used.
        :param str v: value to put
        :return None:
        """
        return put_kv(
            k, v, cas,
            endpoint=join(self.endpoint, 'kv/'),
            timeout=self.timeout
        )

    def put_mapping(self, mapping):
        """
        Atomically (Txn) put a key/value mapping at the configured endpoint
        :param dict mapping: dict of key/values put
        :return None:
        """
        return put_kv_txn(
            mapping,
            endpoint=join(self.endpoint, 'txn/'),
            timeout=self.timeout
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

    def get_cas(self, k=None, recurse=False):
        """
        Get a value for a key and use CAS to guard updates against updates
        from multiple clients.
        :param str k: key to get
        :param bool recurse: return nested entries
        :return dict mapping: retrieved key/value mapping
        """
        return get_kv_cas(
            k=k, recurse=recurse,
            endpoint=join(self.endpoint, 'kv/'),
            timeout=self.timeout
        )

    def get_meta(self, k=None, recurse=False):
        """
        Get the raw un-decoded key value data for a key
        :param str k: key to get
        :param bool recurse: return nested entries
        :return dict: raw API response
        """
        return get_kv_meta(
            k=k, recurse=recurse,
            endpoint=self.endpoint,
            timeout=self.timeout
        )

    def get(self, k=None, recurse=False):
        """
        Get a value for a key or all values under that key if recursive is specified
        :param str k: key to get
        :param bool recurse: return nested entries
        :return dict mapping: retrieved key/value mapping
        """
        return get_kv(
            k=k, recurse=recurse,
            endpoint=join(self.endpoint, 'kv/'),
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
            endpoint=join(self.endpoint, 'kv/'),
            timeout=self.timeout
        )
