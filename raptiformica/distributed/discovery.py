from raptiformica.settings import conf
import raptiformica.settings.load


def host_and_port_pairs_from_config(cached=False):
    """
    Return an iterable of the host and port pairs of the neighbours found in the distributed
    config mapping
    :param bool cached: Only get the host and ports from the local cached config
    :return iterable[tuple, ..] host_and_port_pairs: A list of tuples containing host and ports
    """
    # Absolute import to prevent circular import
    config = raptiformica.settings.load.get_config(cached=cached)
    meshnet_config = config[conf().KEY_VALUE_PATH].get('meshnet', {})
    neighbours = meshnet_config.get('neighbours', {})
    return [(n['host'], n['ssh_port']) for n in neighbours.values()]
