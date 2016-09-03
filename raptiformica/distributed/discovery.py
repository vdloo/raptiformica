from os.path import join

from raptiformica.settings import KEY_VALUE_PATH
from raptiformica.settings.load import get_config
from raptiformica.utils import startswith


def host_and_port_pairs_from_mutable_config():
    """
    Return an iterable of the host and port pairs of the neighbours found in the distributed
    config mapping
    :return iterable[tuple, ..] host_and_port_pairs: A list of tuples containing host and ports
    """
    mapped = get_config()
    neighbour_kv_path = '{}/meshnet/neighbours/'.format(
        KEY_VALUE_PATH
    )
    neighbours = set(
        map(
            lambda x: x.split('/')[3],
            filter(
                startswith(neighbour_kv_path),
                mapped
            )
        )
    )

    neighbour_paths = map(
        lambda neighbour: join(neighbour_kv_path, neighbour),
        neighbours
    )

    return map(
        lambda np: (
            mapped[join(np, 'host')], mapped[join(np, 'ssh_port')]
        ),
        neighbour_paths
    )
