from raptiformica.settings.load import load_config
from raptiformica.utils import keys_sorted


def list_types_from_config(item):
    """
    List types from config.
    :param str item: name of the type. i.e. 'server_types'
    :return list types: list of all the types like ['headless, 'workstation']
    """
    config = load_config()
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
