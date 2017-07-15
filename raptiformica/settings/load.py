from contextlib import suppress, contextmanager
from fcntl import LOCK_EX, flock, LOCK_UN
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
from raptiformica.settings import conf

from raptiformica.utils import load_json, write_json, list_all_files_with_extension_in_directory, ensure_directory
import raptiformica.distributed.proxy

log = getLogger(__name__)

consul_conn = Connection(
    endpoint=conf().KEY_VALUE_ENDPOINT,
    timeout=conf().KEY_VALUE_TIMEOUT
)

API_EXCEPTIONS = (HTTPError, HTTPException, URLError,
                  ConnectionRefusedError, ConnectionResetError,
                  BadStatusLine, OSError, ValueError)


@contextmanager
def config_cache_lock():
    """
    Obtain the config cache lock, perform the code
    in the context and then let the lock go.
    :yield None
    :return None:
    """
    with open(conf().CONFIG_CACHE_LOCK, 'w+') as lock:
        try:
            log.debug(
                "Getting config cache lock. "
                "If this blocks forever, try deleting file "
                "{} and restart the process.".format(conf().CONFIG_CACHE_LOCK)
            )
            flock(lock, LOCK_EX)  # Blocks until lock becomes available
            yield
        finally:
            log.debug("Releasing the config cache lock")
            flock(lock, LOCK_UN)


def write_config_mapping(config, config_file):
    """
    Write the config to a config file
    :param dict config: The config to be dumped to json
    :param str config_file: The mutable config file
    :return None:
    """
    ensure_directory(conf().ABS_CACHE_DIR)
    # Lock the config cache file so two processes can't
    # write to the file at the same time and corrupt the json
    with config_cache_lock():
        write_json(config, config_file)


def load_module_config(modules_dir=None):
    """
    Find all configuration files in the modules_dir and return them as parsed a list
    :param str modules_dir: path to look for .json config files in
    :return list configs: list of parsed configs
    """
    modules_dir = modules_dir or conf().MODULES_DIR
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


def load_module_configs(module_dirs=None):
    """
    Load the module configs for all the specified modules dirs and
    return a flattened list containing the configs
    :param iterable module_dirs: directories to look for module configs in
    :return list configs: list of parsed configs
    """
    module_dirs = module_dirs or (conf().MODULES_DIR, conf().USER_MODULES_DIR)
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
        if conf().FORWARDED_CONSUL_ONCE_ALREADY:
            log.debug(
                "Not attempting to forward any remote Consul instance, "
                "already attempted that once. Working from the most recent "
                "available cached config now"
            )
        else:
            log.debug("Attempting API call on remote Consul instance")
            conf().set_forwarded_remote_consul_once()
            with suppress(RuntimeError):
                # Absolute import because the distributed proxy
                # imports from settings as well
                with raptiformica.distributed.proxy.forward_any_port(
                    source_port=8500, predicate=[
                        'consul', 'kv', 'get', '/raptiformica/raptiformica_api_version'
                    ]
                ):
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
    mapping = try_config_request(
        lambda: consul_conn.get_mapping(conf().KEY_VALUE_PATH)
    )
    if not mapping:
        raise ValueError(
            "Retrieved empty data from distributed key "
            "value store. Not accepting."
        )
    if not validate_config_mapping(mapping):
        raise ValueError(
            "Retrieved corrupted data from distributed key "
            "value store. Not accepting."
        )
    return mapping


def on_disk_mapping(module_dirs=None):
    """
    Retrieve the on disk config mapping
    :param iterable module_dirs: directories to look for module configs in
    :return dict mapping: retrieved key value mapping with config data
    """
    module_dirs = module_dirs or (conf().MODULES_DIR, conf().USER_MODULES_DIR)
    configs = load_module_configs(module_dirs=module_dirs)
    return {
        join(conf().KEY_VALUE_PATH, k): v for k, v in
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
        consul_conn.delete(key, recurse=recurse)
        sync_shared_config_mapping()
    except API_EXCEPTIONS:
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
    if not validate_config_mapping(mapping):
        raise RuntimeError(
            "Missing all required service types from config. "
            "It might have gotten corrupted. "
            "Refusing to cache this mapping!"
        )
    write_config_mapping(mapping, conf().MUTABLE_CONFIG)


def cached_config_mapping():
    """
    Retrieve the cached config of the last successful config download
    from distributed key value store. Waits with reading the cached
    config until the exclusive lock can be acquired to prevent reading
    truncated json because another process could be updating the cache.
    :return dict mapping: the k v config mapping
    """
    with config_cache_lock():
        return load_json(conf().MUTABLE_CONFIG)


def validate_config_mapping(mapping):
    """
    Validate a config mapping. If for some reason the retrieved mapping is
    corrupted we need to act accordingly.
    :param dict mapping: key value mapping with config data
    :return bool valid: True if valid, False if not
    """
    mapping_as_dict = dictionary_map(mapping)
    for config_type in ('server', 'compute', 'platform'):
        if config_type not in mapping_as_dict[conf().KEY_VALUE_PATH]:
            return False
    return True


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
        remove(conf().MUTABLE_CONFIG)


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
        rmtree(conf().USER_ARTIFACTS_DIR, ignore_errors=True)
    if purge_modules:
        log.info("Purging user modules")
        rmtree(conf().USER_MODULES_DIR, ignore_errors=True)


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
