from itertools import chain
from json import loads
from base64 import b64decode
from os.path import join
from urllib.error import URLError, HTTPError
from urllib import request
from logging import getLogger

from raptiformica.settings import MODULES_DIR, ABS_CACHE_DIR, KEY_VALUE_ENDPOINT, \
    KEY_VALUE_PATH, USER_MODULES_DIR, MUTABLE_CONFIG
from raptiformica.utils import load_json, write_json, \
    list_all_files_with_extension_in_directory, ensure_directory

log = getLogger(__name__)


def write_config(config, config_file):
    """
    Write the config to a config file
    :param dict config: The config to be dumped to json
    :param str config_file: The mutable config file
    :return None:
    """
    ensure_directory(ABS_CACHE_DIR)
    write_json(config, config_file)


def load_module_config(modules_dir=MODULES_DIR):
    """
    Find all configuration files in the modules_dir and return them as parsed a list
    :param str modules_dir: path to look for .json config files in
    :return list configs: list of parsed configs
    """
    file_names = list_all_files_with_extension_in_directory(
        modules_dir, 'json'
    )

    def try_load_module(filename):
        log.debug("Loading module config from {}".format(filename))
        try:
            return load_json(filename)
        except ValueError:
            log.warning("Failed to parse module config in {}, "
                        "skipping..".format(filename))
    return filter(lambda x: x is not None, map(try_load_module, file_names))


def load_module_configs(module_dirs=(MODULES_DIR, USER_MODULES_DIR)):
    """
    Load the module configs for all the specified modules dirs and
    return a flattened list containing the configs
    :param iterable module_dirs: directories to look for module configs in
    :return list configs: list of parsed configs
    """
    return chain.from_iterable(
        map(load_module_config, module_dirs)
    )


def loop_config(config, path='/', callback=lambda path, k, v: None):
    """
    Loop the config and perform the callback for each value
    :param dict config: config to loop for values
    :param str path: the depth in the dict joined by /
    :param func callback: the callback to perform for each value
    :return None:
    """
    for k, v in config.items():
        if isinstance(v, dict):
            loop_config(v, path=join(path, k), callback=callback)
        else:
            callback(path, k, v)


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
    req = request.Request(url=url, data=encoded, method='PUT')
    with request.urlopen(req) as f:
        log.debug("PUT k v pair ({}, {}) to {}: {}, {}".format(
            k, v, url, f.status, f.reason
        ))


def upload_config(mapped):
    """
    Upload a mapped config to the distributed key value store
    :param iterable[dict, ..] mapped: list of key value pairs
    :return None:
    """
    log.debug("Uploading local configs to distributed key value store")
    for key, value in mapped.items():
        put_kv(KEY_VALUE_ENDPOINT, key, value)


def download_config():
    """
    Get the entire config from the distributed key value store
    :return dict mapping: all registered key value pairs
    """
    log.debug(
        "Attempting to retrieve the shared config "
        "from the distributed key value store"
    )
    endpoint = join(KEY_VALUE_ENDPOINT, KEY_VALUE_PATH)
    recurse_kv = join(endpoint, '?recurse')
    req = request.Request(url=recurse_kv, method='GET')
    with request.urlopen(req) as r:
        result = loads(r.read().decode('utf-8'))
    mapping = {r['Key']: b64decode(r['Value']).decode('utf-8') for r in result}
    return mapping


def map_configs(configs):
    """
    Map the module configs to the key value associative array
    :param iterable[dict, ..] configs: list of configs to map as key value pairs
    :return dict mapping: key value mapping with config data
    """
    d = dict()
    for config in configs:
        loop_config(
            config,
            path=join(KEY_VALUE_ENDPOINT, KEY_VALUE_PATH),
            callback=lambda path, k, v: d.update(
                {join(path.replace(KEY_VALUE_ENDPOINT, ''), k): v}
            )
        )
    return d


def on_disk_mapping():
    """
    Retrieve the on disk config mapping
    :return dict mapping: retrieved key value mapping with config data
    """
    configs = load_module_configs()
    return map_configs(configs)


def try_update_config(mapping):
    """
    If no consul cluster has been established yet there is no
    distributed key value store yet, in that case write the mapping
    to the local cache so this can be copied by rsync to new hosts
    until at least three can be linked together and form consensus
    :param dict mapping: key value mapping with config data
    :return dict mapping: retrieved key value mapping with config data
    """
    try:
        mapping = update_config(mapping)
    except (HTTPError, URLError, ConnectionRefusedError):
        cached_mapping = get_config()
        cached_mapping.update(mapping)
        cache_config(cached_mapping)
        mapping = cached_mapping
    return mapping


def update_config(mapping):
    """
    Upload a new mapping to the distributed key value store and
    retrieve the latest mapping
    :param dict mapping: the mapping to PUT to the k v API
    :return dict mapping: retrieved key value mapping with config data
    """
    upload_config(mapping)
    return download_config()


def sync_shared_config_mapping():
    """
    Retrieve the remote config mapping or upload
    the local configuration mapping if none exists in
    the distributed key value store yet. Also caches
    the downloaded result.
    :return dict mapping: retrieved key value mapping with config data
    """
    try:
        mapping = download_config()
    except HTTPError:
        mapping = get_local_config()
        mapping = update_config(mapping)
    cache_config(mapping)
    return mapping


def cache_config(mapping):
    """
    Write the retrieved config to disk so the mutations are retained
    even in case of network failure
    :param dict mapping: the cached k v mapping
    :return None:
    """
    if not mapping:
        raise RuntimeError(
            "Passed key value mapping was null. "
            "Refusing to cache empty mapping!"
        )
    write_config(mapping, MUTABLE_CONFIG)


def cached_config():
    """
    Retrieve the cached config of the last successful config download
    from distributed key value store
    :return dict mapping: the k v config mapping
    """
    return load_json(MUTABLE_CONFIG)


def get_local_config():
    """
    Get the local config, either from cache or from the mapped modules
    :return dict mapping: key value mapping with config data
    """
    failed_cached_config = "No cache is available. Returning the mapped " \
                           "configs on disk."
    try:
        return cached_config()
    except FileNotFoundError:
        log.debug(failed_cached_config)
        return on_disk_mapping()


def get_config():
    """
    Get the most recent config we can
    - check if we can download the mapping from the distributed
    key value store
    - if we can not, try uploading the config mapping on disk
    - if we can not, try returning a cached config
    - if there is no cached config, return the config mapping on disk
    :return dict mapping: key value mapping with config data
    """
    failed_distributed_config = "Failed to retrieve the config from the " \
                                "distributed key value store, will try " \
                                "to get the latest state from the cache now."
    try:
        return sync_shared_config_mapping()
    except URLError:
        log.debug(failed_distributed_config)
        return get_local_config()
