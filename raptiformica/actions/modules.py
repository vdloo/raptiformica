from os.path import join
from logging import getLogger

from shutil import rmtree

from raptiformica.settings import conf
from raptiformica.settings.load import on_disk_mapping, try_delete_config, try_update_config_mapping
from raptiformica.shell.git import clone_source

log = getLogger(__name__)


def determine_clone_data(name):
    """
    Compose a triple of git repo and checkout name
    :param str name: name of the module to compose the clone data for
    :return tuple[str, str]: Tuple of the url to clone and the relative
    directory it should be cloned to
    """
    parts = name.split('/')
    if len(parts) == 2:
        url = join("https://github.com", name)
    else:
        url = name
    return (
        url,
        parts[-1].replace('.git', '')
    )


def retrieve_module(module_name):
    """
    Copy the module to the ~/.raptiformica/modules directory
    :param str module_name: name of the module to retrieve
    :return None:
    """
    log.info("Checking out {}".format(module_name))
    url, directory = determine_clone_data(module_name)
    log.debug("Cloning from {}".format(url))
    clone_source(
        url,
        join(conf().USER_MODULES_DIR, directory)
    )


def load_configs(module_name):
    """
    Load the module configs into the key value mapping
    :param str module_name: name of the module to load from disk
    :return:
    """
    _, directory = determine_clone_data(module_name)
    module_directory = join(conf().USER_MODULES_DIR, directory)
    mapping = on_disk_mapping(module_dirs=(module_directory,))
    log.debug("Loading keys for {} into the config".format(module_name))
    try_update_config_mapping(mapping)


def remove_keys(mapping, module_directory):
    """
    Remove the keys in the provided mapping from the config
    :param str module_directory: directory of the module of
    which the keys to remove
    :param dict mapping: k v mapping to remove
    :return:
    """
    log.debug("Removing associated keys from the config")
    for key in mapping:
        try_delete_config(key)
    log.debug(
        "Ensuring module directory is removed"
    )
    rmtree(
        module_directory,
        ignore_errors=True
    )


def refresh_keys(mapping):
    """
    Refresh the keys in the mapping with the current config on disk.
    This makes sure keys previously overwritten with a user module
    are restored to the default config.
    :param dict mapping: k v mapping to refresh
    :return:
    """
    new_mapping = on_disk_mapping()
    mapping_to_update = dict()
    for key in mapping:
        updated_value = new_mapping.get(key)
        if updated_value:
            mapping_to_update[key] = updated_value
    try_update_config_mapping(mapping_to_update)


def unload_module(module_name):
    """
    Unload a module from the system
    :param str module_name: name of the module to unload
    :return None:
    """
    _, directory = determine_clone_data(module_name)
    module_directory = join(conf().USER_MODULES_DIR, directory)
    mapping = on_disk_mapping(module_dirs=(module_directory,))
    remove_keys(mapping, module_directory)
    refresh_keys(mapping)


def load_module(module_name):
    """
    Load a module into the system
    :param str module_name: name of the module to load
    :return None:
    """
    log.debug("Trying to unload old version")
    unload_module(module_name)
    retrieve_module(module_name)
    load_configs(module_name)
