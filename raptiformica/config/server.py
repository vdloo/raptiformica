from raptiformica.utils import load_config


def get_server_types():
    """
    Parse server types from config and return them as a list
    :return list[str] server_types: all server types from the configuration
    """
    config = load_config()
    return list(config.get('server_types', {}).keys())


def get_first_server_type():
    """
    Get the first server type from the configuration, if there is none throw a ValueError
    :return str: server_type
    """
    server_types = get_server_types()
    if len(server_types) == 0:
        raise ValueError(
            "You need to have at least one server type configured. Check your config file"
        )
    return server_types[0]
