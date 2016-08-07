from logging import getLogger

from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.load import load_config
from raptiformica.utils import keys_sorted

log = getLogger(__name__)


def list_types_from_config(item):
    """
    List types from config.
    :param str item: name of the type. i.e. 'server_types'
    :return list types: list of all the types like ['headless, 'workstation']
    """
    config = load_config(MUTABLE_CONFIG)
    return keys_sorted(config, item)


def get_compute_types():
    """
    Parse compute types from config and return them as a list
    :return list[str] server_types: all compute types from the configuration
    """
    return list_types_from_config('compute_types')


def get_server_types():
    """
    Parse server types from config and return them as a list
    :return list[str] server_types: all server types from the configuration
    """
    return list_types_from_config('server_types')


def get_first_from_types(item):
    """
    Get the first type from the configuration, if there is none throw a ValueError
    :param str item: name of the type. i.e. 'server_types'
    :return str: type_name
    """
    types = list_types_from_config(item)
    if len(types) == 0:
        raise ValueError(
            "You need to have at least one {} configured. "
            "Check your config file".format(item)
        )
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


def verify_server_type_implemented_in_compute_type(compute_type_config, server_type):
    """
    Error out when there is no such server type configured for the specified compute type
    :param dict compute_type_config: the compute type config for a specific compute type
    :param str server_type: name of the server type to provision the machine as
    :return None:
    """
    if server_type not in compute_type_config:
        log.error("This compute type has no implementation for server type {}! "
                  "Check your config".format(server_type))
        exit(1)


def retrieve_compute_type_config_for_server_type(server_type=get_first_server_type(),
                                                 compute_type=get_first_compute_type()):
    """
    Load the config for server_type as defined in the config for compute_type
    :param str compute_type: name of the compute type to start an instance on
    :param str server_type: name of the server type to provision the machine as
    :return dict config: the server_type config in the compute_type_config
    """
    config = load_config(MUTABLE_CONFIG)
    compute_type_config = config['compute_types'][compute_type]
    verify_server_type_implemented_in_compute_type(
        compute_type_config, server_type
    )
    return compute_type_config[server_type]
