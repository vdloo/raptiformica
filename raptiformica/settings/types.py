from functools import partial
from logging import getLogger

from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.load import load_config, merge_module_configs
from raptiformica.shell.types import check_type_available
from raptiformica.utils import keys_sorted, find_key_in_dict_recursively

log = getLogger(__name__)


def list_types_from_config(item):
    """
    List types from config.
    :param str item: name of the type. i.e. 'server_types'
    :return list types: list of all the types like ['headless, 'workstation']
    """
    config = load_config(MUTABLE_CONFIG)
    return keys_sorted(config, item)


def get_available_types_for_item(item):
    """
    Get all available types from a type
    :param str item: name of the type. i.e. 'server_types'
    :return list types: list of all available types like ['headless, 'workstation']
    """
    return list(filter(
        partial(check_type_available, item),
        list_types_from_config(item)
    ))


def get_compute_types():
    """
    Parse compute types from config and return them as a list
    :return list[str] server_types: all compute types from the configuration
    """
    return get_available_types_for_item('compute_types')


def get_server_types():
    """
    Parse server types from config and return them as a list
    :return list[str] server_types: all server types from the configuration
    """
    return get_available_types_for_item('server_types')


def get_first_from_types(item):
    """
    Get the first type from the configuration, if there is none throw a ValueError
    :param str item: name of the type. i.e. 'server_types'
    :return str: type_name
    """
    types = get_available_types_for_item(item)
    if len(types) == 0:
        log.warning(
            "You need to have at least one available type configured for {}. \n"
            "Do you have the required dependencies installed? "
            "Check your config file".format(item)
        )
        exit(1)
    return types[0]


def get_first_server_type():
    """
    Get the first server type from the configuration, if there is none throw a ValueError
    :return str server_type: the first server type
    """
    return get_first_from_types('server_types')


def get_first_compute_type():
    """
    Get the first compute type from the configuration, if there is none throw a ValueError
    :return str compute_type: the first compute type
    """
    return get_first_from_types('compute_types')


def get_first_platform_type():
    """
    Get the first platform type from the configuration, if there is none throw a ValueError
    :return str platform_type: the first platform type
    """
    return get_first_from_types('platform_types')


def verify_server_type_implemented_in_compute_type(compute_type_config, server_type):
    """
    Error out when there is no such server type configured for the specified compute type
    :param dict compute_type_config: the compute type config for a specific compute type
    :param str server_type: name of the server type to provision the machine as
    :return dict server_type_implementation_config:
    """
    server_type_implementation_config = find_key_in_dict_recursively(
        compute_type_config, server_type
    )
    if not server_type_implementation_config:
        log.error("This compute type has no implementation for server type {}! "
                  "Check your config".format(server_type))
        exit(1)
    return merge_module_configs(server_type_implementation_config)


def retrieve_compute_type_config_for_server_type(server_type=None, compute_type=None):
    """
    Load the config for server_type as defined in the config for compute_type
    :param str compute_type: name of the compute type to start an instance on
    :param str server_type: name of the server type to provision the machine as
    :return dict config: the server_type config in the compute_type_config
    """
    server_type = server_type or get_first_server_type()
    compute_type = compute_type or get_first_compute_type()
    config = load_config(MUTABLE_CONFIG)
    compute_type_config = config['compute_types'][compute_type]
    return verify_server_type_implemented_in_compute_type(
        compute_type_config, server_type
    )
