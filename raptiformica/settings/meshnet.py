import uuid
from os.path import join
from logging import getLogger

from raptiformica.actions.prune import ensure_neighbour_removed_from_config_by_host
from raptiformica.distributed.events import send_reload_meshnet
from raptiformica.distributed.ping import find_host_that_can_ping
from raptiformica.settings import conf
from raptiformica.settings.load import get_config_mapping, try_update_config_mapping
from raptiformica.shell import cjdns
from raptiformica.shell.raptiformica import inject

log = getLogger(__name__)


def ensure_shared_secret(service):
    """
    Ensure a key 'password' exists in the config for a specific meshnet service.
    If no key exists, create it with a new (psuedo) random value
    :param str service: name of the service to ensure a secret for
    :return dict mapping: the updated config mapping
    """
    mapping = get_config_mapping()
    shared_secret_path = "{}/meshnet/{}/password".format(
        conf().KEY_VALUE_PATH, service
    )
    if not mapping.get(shared_secret_path):
        log.info("Generating new {} secret".format(service))
        mapping = try_update_config_mapping({
            shared_secret_path: uuid.uuid4().hex
        })
    return mapping


def update_cjdns_config():
    """
    Ensure a key 'password' exists in the config for the cjdns item in the meshnet config
    If no key exists, create it with a new (psuedo) random value
    :return dict mapping: the updated config mapping
    """
    return ensure_shared_secret('cjdns')


def update_consul_config():
    """
    Ensure a key 'password' exists in the config for the consul item in the meshnet config
    If no key exists, create it with a new (psuedo) random value
    :return dict mapping: the updated config mapping
    """
    return ensure_shared_secret('consul')


def update_neighbours_config(host, port=22, uuid=None):
    """
    Update the neighbours config in the k v mapping
    - update the distributed key value store with the neighbour
    - if the k v store can not be reached, update the local cached mapping
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str uuid: identifier for a local compute checkout
    :return dict mapping: the updated config mapping
    """
    cjdns_public_key = cjdns.get_public_key(host, port=port)
    cjdns_ipv6_address = cjdns.get_ipv6_address(host, port=port)

    neighbour_entry = {
        'host': host,
        'cjdns_port': conf().CJDNS_DEFAULT_PORT,
        'cjdns_public_key': cjdns_public_key,
        'cjdns_ipv6_address': cjdns_ipv6_address,
        # todo: get this port dynamically from the cjdroute.conf
        'ssh_port': port,
    }
    if uuid:
        neighbour_entry['uuid'] = uuid

    neighbour_path = "{}/meshnet/neighbours/{}/".format(
        conf().KEY_VALUE_PATH, cjdns_public_key
    )
    neighbour_mapping = {
        join(neighbour_path, k): v for k, v in neighbour_entry.items()
    }
    ensure_neighbour_removed_from_config_by_host(host)
    return try_update_config_mapping(neighbour_mapping)


def update_meshnet_config(host, port=22, compute_checkout_uuid=None):
    """
    Add a host to the distributed key value config mapping
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str compute_checkout_uuid: identifier for a local compute checkout
    :return None:
    """
    log.info("Updating meshnet config with data from host {}".format(
        host
    ))
    update_cjdns_config()
    update_consul_config()
    update_neighbours_config(
        host, port=port, uuid=compute_checkout_uuid
    )


def bootstrap_host_to_neighbour(host, port, connected_host, connected_host_port):
    """
    Bootstrap a consul cluster by injecting a host into a neighbours meshnet
    config to bootstrap consensus if no consensus has been established yet.
    :param str host: The host to inject
    :param int port: The ssh port of the host to inject
    :param connected_host: The host to inject the specified host on
    :param connected_host_port: The ssh port of the host to inject the
    specified host on
    :return None:
    """
    log.info(
        "Injecting the new host into its meshnet config "
        "to bootstrap the cluster if needed."
    )
    inject(host, port, connected_host, connected_host_port)


def ensure_route_to_new_neighbour(
    host, port=22, compute_checkout_uuid=None
):
    """
    Add a host to the distributed network by updating the distributed config
    and sending an update event to all neighbours. If no consensus has been
    established yet, add the neighbour to the local config and try to find a
    connected neighbour that can access the new machine and add a route there.
    That last part is needed because otherwise instances won't be able to
    connect back from beyond a firewall (in case of not being able to connect
    directly from the client) as long as no consensus has been established.
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str compute_checkout_uuid: identifier for a local compute checkout
    :return None:
    """
    update_meshnet_config(
        host, port=port, compute_checkout_uuid=compute_checkout_uuid
    )
    connected_host, connected_host_port = find_host_that_can_ping(host)
    if connected_host:
        log.info("Found peer that can connect directly to the new neighbour")
        bootstrap_host_to_neighbour(
            host, port, connected_host, connected_host_port
        )
    else:
        log.info(
            "Found no neighbour that could already connect "
            "directly to the new host {}. Sending reload event "
            "and hoping for the best..".format(host)
        )
    send_reload_meshnet()
