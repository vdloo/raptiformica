from functools import partial
from logging import getLogger

from raptiformica.settings import KEY_VALUE_PATH
from raptiformica.settings.load import get_config
from raptiformica.shell.types import check_type_available
from raptiformica.utils import startswith

log = getLogger(__name__)


def list_types_from_config(item):
    """
    List types from config.
    :param str item: name of the type. i.e. 'server_types'
    :return set types: set of all the types for the item like ['headless, 'workstation']
    """
    mapped = get_config()
    return set(
        map(
            lambda x: x.split('/')[2],
            filter(
                startswith('{}/{}/'.format(KEY_VALUE_PATH, item)),
                mapped
            )
        )
    )


def get_available_types_for_item(item):
    """
    Get all available types from a type
    :param str item: name of the type. i.e. 'server_types'
    :return list types: list of all available types like ['headless, 'workstation']
    """
    return sorted(list(filter(
        partial(check_type_available, item),
        list_types_from_config(item)
    )))


def get_compute_types():
    """
    Parse compute types from config and return them as a list
    :return list[str] server_types: all compute types from the configuration
    """
    return get_available_types_for_item('compute')


def get_server_types():
    """
    Parse server types from config and return them as a list
    :return list[str] server_types: all server types from the configuration
    """
    return get_available_types_for_item('server')


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
    return get_first_from_types('server')


def get_first_compute_type():
    """
    Get the first compute type from the configuration, if there is none throw a ValueError
    :return str compute_type: the first compute type
    """
    return get_first_from_types('compute')


def get_first_platform_type():
    """
    Get the first platform type from the configuration, if there is none throw a ValueError
    :return str platform_type: the first platform type
    """
    return get_first_from_types('platform')


def retrieve_compute_type_config_for_server_type(server_type=None, compute_type=None):
    """
    Load the config for server_type as defined in the config for compute_type
    Error out when there is no such server type configured for the specified compute type
    :param str compute_type: name of the compute type to start an instance on
    :param str server_type: name of the server type to provision the machine as
    :return dict config: the server_type config in the compute_type_config
    """
    server_type = server_type or get_first_server_type()
    compute_type = compute_type or get_first_compute_type()
    mapped = get_config()
    compute_type_config_for_server_type = list(filter(
        startswith("{}/compute/{}/{}/".format(
            KEY_VALUE_PATH, compute_type, server_type
        )),
        mapped
    ))
    if not compute_type_config_for_server_type:
        raise RuntimeError(
            "This compute type has no implementation "
            "for server type {}!".format(server_type)
        )
    return {k: mapped[k] for k in compute_type_config_for_server_type}
