from logging import getLogger

from raptiformica.actions.mesh import join_meshnet, configure_cjdroute_conf, configure_consul_conf, ensure_cjdns_routing
from raptiformica.distributed.discovery import host_and_port_pairs_from_config
from raptiformica.distributed.members import try_get_members_list

log = getLogger(__name__)


def show_members():
    """
    Print the members list. For now a wrapper around 'consul members'
    :return None:
    """
    host_and_port_pairs = host_and_port_pairs_from_config()
    members_list = try_get_members_list(host_and_port_pairs)
    if members_list:
        print(members_list)


def rejoin_members():
    """
    Attempt to join all the members found in the available config
    :return None:
    """
    configure_cjdroute_conf()
    configure_consul_conf()
    ensure_cjdns_routing()
    join_meshnet()
