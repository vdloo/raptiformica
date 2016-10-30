from contextlib import suppress
from functools import reduce
from http.client import HTTPException, BadStatusLine
from itertools import chain
from os.path import join
from os import remove
from urllib.error import URLError, HTTPError
from logging import getLogger

from shutil import rmtree

from consul_kv import Connection, map_dictionary, dictionary_map
from consul_kv.utils import dict_merge
from raptiformica.distributed.proxy import forward_any_port

from raptiformica.settings import MODULES_DIR, ABS_CACHE_DIR, KEY_VALUE_ENDPOINT, \
    KEY_VALUE_PATH, USER_MODULES_DIR, MUTABLE_CONFIG, USER_ARTIFACTS_DIR, KEY_VALUE_TIMEOUT
from raptiformica.utils import load_json, write_json, list_all_files_with_extension_in_directory, ensure_directory

log = getLogger(__name__)

consul_conn = Connection(
    endpoint=KEY_VALUE_ENDPOINT,
    timeout=KEY_VALUE_TIMEOUT
)

API_EXCEPTIONS = (HTTPError, HTTPException, URLError,
                  ConnectionRefusedError, ConnectionResetError,
                  BadStatusLine, OSError)


def write_config_mapping(config, config_file):
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
            config = load_json(filename)
            if 'raptiformica_api_version' not in config:
                raise ValueError(
                    "Not a raptiformica config file. Skipping.."
                )
            return config
        except ValueError:
            log.debug("Failed to parse module config in {}, "
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


def try_config_request(func):
    """
    Try the config request on the local Consul instance's API port,
    if that fails attempt the same request on the API port of one of
    the locally known neighbours.
    :param func func: Function to attempt
    :return dict mapping: The function result
    """
    try:
        log.debug("Attempting API call on local Consul instance")
        return func()
    except API_EXCEPTIONS:
        log.debug("Attempting API call on remote Consul instance")
        with suppress(RuntimeError):
            with forward_any_port(source_port=8500, predicate=['consul', 'members']):
                return func()
        raise


def upload_config_mapping(mapped):
    """
    Upload a mapped config to the distributed key value store
    :param iterable[dict, ..] mapped: list of key value pairs
    :return None:
    """
    log.debug("Uploading local configs to distributed key value store")
    try_config_request(lambda: consul_conn.put_mapping(mapped))


def download_config_mapping():
    """
    Get the entire config from the distributed key value store
    :return dict mapping: all registered key value pairs
    """
    log.debug(
        "Attempting to retrieve the shared config "
        "from the distributed key value store"
    )
    return try_config_request(lambda: consul_conn.get_mapping(KEY_VALUE_PATH))


def on_disk_mapping(module_dirs=(MODULES_DIR, USER_MODULES_DIR)):
    """
    Retrieve the on disk config mapping
    :param iterable module_dirs: directories to look for module configs in
    :return dict mapping: retrieved key value mapping with config data
    """
    configs = load_module_configs(module_dirs=module_dirs)
    return {
        join(KEY_VALUE_PATH, k): v for k, v in
        reduce(dict_merge, map(map_dictionary, configs), dict()).items()
    }


def try_update_config_mapping(mapping):
    """
    If no consul cluster has been established yet there is no
    distributed key value store yet, in that case write the mapping
    to the local cache so this can be copied by rsync to new hosts
    until at least three can be linked together and form consensus
    :param dict mapping: key value mapping with config data
    :return dict mapping: retrieved key value mapping with config data
    """
    try:
        mapping = update_config_mapping(mapping)
    except API_EXCEPTIONS:
        cached_mapping = get_config_mapping()
        cached_mapping.update(mapping)
        cache_config_mapping(cached_mapping)
        mapping = cached_mapping
    return mapping


def try_delete_config(key, recurse=False):
    """
    Try to delete a key in the distributed key value store,
    if there is no distributed key value store yet or we can't
    connect, then remove the key from the local config.
    :param str key: key to remove
    :param bool recurse: recurse the path and delete all entries
    :return:
    """
    # todo: in the case of an offline delete those changes will
    # never be synced back to the distributed k v store but
    # should instead be fixed by some form of eventual consistency
    try:
        path = join(KEY_VALUE_ENDPOINT, key)
        consul_conn.delete(path, recurse=recurse)
        sync_shared_config_mapping()
    except URLError:
        log.debug(
            "Could not connect to the distributed key value store to "
            "delete the key. Only deleting from local cache for now."
        )
        cached_mapping = get_config_mapping()
        mapping = {
            k: v for k, v in cached_mapping.items() if
            # find all keys starting with the key if recurse,
            # else only filter away the key with an exact match
            not (k.startswith(key) if recurse else k == key)
        }
        cache_config_mapping(mapping)


def update_config_mapping(mapping):
    """
    Upload a new mapping to the distributed key value store and
    retrieve the latest mapping
    :param dict mapping: the mapping to PUT to the k v API
    :return dict mapping: retrieved key value mapping with config data
    """
    upload_config_mapping(mapping)
    return download_config_mapping()


def sync_shared_config_mapping():
    """
    Retrieve the remote config mapping or upload
    the local configuration mapping if none exists in
    the distributed key value store yet. Also caches
    the downloaded result.
    :return dict mapping: retrieved key value mapping with config data
    """
    try:
        mapping = download_config_mapping()
    except HTTPError:
        mapping = get_local_config_mapping()
        mapping = update_config_mapping(mapping)
    cache_config_mapping(mapping)
    return mapping


def cache_config_mapping(mapping):
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
    write_config_mapping(mapping, MUTABLE_CONFIG)


def cached_config_mapping():
    """
    Retrieve the cached config of the last successful config download
    from distributed key value store
    :return dict mapping: the k v config mapping
    """
    return load_json(MUTABLE_CONFIG)


def get_local_config_mapping():
    """
    Get the local config, either from cache or from the mapped modules
    :return dict mapping: key value mapping with config data
    """
    failed_cached_config = "No cache is available. Returning the mapped " \
                           "configs on disk."
    try:
        return cached_config_mapping()
    except FileNotFoundError:
        log.debug(failed_cached_config)
        return on_disk_mapping()


def purge_local_config_mapping():
    """
    Remove the local config mapping if it exists
    :return None:
    """
    log.info("Puring locally cached config")
    with suppress(FileNotFoundError):
        remove(MUTABLE_CONFIG)


def purge_config(purge_artifacts=False, purge_modules=False):
    """
    Remove local artifacts
    :param bool purge_artifacts: Remove all stored artifacts
    :param bool purge_modules: Remove all installed modules
    :return None:
    """
    purge_local_config_mapping()
    if purge_artifacts:
        log.info("Purging cached artifacts")
        rmtree(USER_ARTIFACTS_DIR, ignore_errors=True)
    if purge_modules:
        log.info("Purging user modules")
        rmtree(USER_MODULES_DIR, ignore_errors=True)


def get_config_mapping():
    """
    Get the most recent config mapping we can
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
    except API_EXCEPTIONS:
        log.debug(failed_distributed_config)
        return get_local_config_mapping()


def get_config(cached=False):
    """
    Get the config mapping and return it as a dict
    :param bool cached: Force using the cached config instead
    of retrieving it from the distributed key value store if
    we can.
    :return dict config: The retrieved config as a dict
    """
    mapping = get_local_config_mapping() if cached else get_config_mapping()
    return dictionary_map(mapping)
