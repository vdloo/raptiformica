from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.load import load_config


def host_and_port_pairs_from_mutable_config():
    """
    Return a list of the host and port pairs of the neighbours found in the local mutable_config
    :return list[tuple, ..] host_and_port_pairs: A list of tuples containing host and ports
    """
    config = load_config(MUTABLE_CONFIG)
    neighbours = config['meshnet']['neighbours']
    return [(neighbour['host'], neighbour['ssh_port']) for neighbour in neighbours.values()]
