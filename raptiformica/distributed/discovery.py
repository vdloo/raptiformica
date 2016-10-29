from raptiformica.settings import KEY_VALUE_PATH
from raptiformica.settings.load import get_config


def host_and_port_pairs_from_config():
    """
    Return an iterable of the host and port pairs of the neighbours found in the distributed
    config mapping
    :return iterable[tuple, ..] host_and_port_pairs: A list of tuples containing host and ports
    """
    config = get_config()
    neighbours = config[KEY_VALUE_PATH]['meshnet']['neighbours']
    return [(n['host'], n['ssh_port']) for n in neighbours.values()]
