from base64 import b64decode
from json import loads
from os.path import join
from urllib import request
from logging import getLogger

log = getLogger(__name__)


def put_kv(path, k, v):
    """
    Put a key and value to the distributed key value store at the location path
    :param str path: api path to PUT to
    :param str k: the key to put
    :param str v: the value to put
    :return None:
    """
    encoded = str.encode(str(v))
    url = join(path, k)
    req = request.Request(
        url=url, data=encoded, method='PUT'
    )
    with request.urlopen(req) as f:
        log.debug("PUT k v pair ({}, {}) to {}: {}, {}".format(
            k, v, url, f.status, f.reason
        ))


def get_kv(path, recurse=False):
    """
    Get the key value mapping from the distributed key value store
    :param str path: path to get the value from
    :param bool recurse: whether or not to recurse over the path and
    retrieve all nested values
    :return dict mapping: key value mapping
    """
    req = request.Request(
        url=join(path, '?recurse') if recurse else path,
        method='GET'
    )
    with request.urlopen(req) as r:
        result = loads(r.read().decode('utf-8'))
    mapping = {
        # values are stored base64 encoded in consul, they
        # are decoded before returned by this function.
        r['Key']: b64decode(r['Value']).decode('utf-8') for r in result
    }
    return mapping


def delete_kv(path, recurse=False):
    """
    Delete a key from the distributed key value mapping
    :param str path: path to the key to remove
    :param bool recurse: recurse the path and delete all entries
    :return:
    """
    req = request.Request(
        url=join(path, '?recurse') if recurse else path,
        method='DELETE'
    )
    with request.urlopen(req) as f:
        log.debug("DELETEd key {}{}: {} {}".format(
            path,
            ' recursively' if recurse else '',
            f.status,
            f.reason
        ))
