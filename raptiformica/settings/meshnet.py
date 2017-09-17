import uuid
from os.path import join
from logging import getLogger
from time import sleep

from raptiformica.actions.prune import ensure_neighbour_removed_from_config_by_host
from raptiformica.distributed.events import send_reload_meshnet
from raptiformica.distributed.ping import find_host_that_can_ping
from raptiformica.settings import conf
from raptiformica.settings.load import get_config_mapping, try_update_config_mapping
from raptiformica.shell import cjdns
from raptiformica.shell.raptiformica import inject
from raptiformica.utils import retry

log = getLogger(__name__)


def retrieve_shared_secret(service, attempts=10):
    """
    Retrieve the shared secret for a service from the distributed
    key value store. If it can't be retrieved or is empty, retry
    it a couple of times just in case there is no consensus in
    the cluster. If we re-create a new secret we split the
    network into a new network because all old nodes if any
    will not be able to authenticate anymore.
    :param str service: name of the service to retrieve a secret for
    :param int attempts: How many attempts left to retrieve the
    shared secret from the distributed key value store.
    :return dict mapping: the retrieved config mapping
    """
    mapping = get_config_mapping()
    shared_secret_path = "{}/meshnet/{}/password".format(
        conf().KEY_VALUE_PATH, service
    )
    if not mapping.get(shared_secret_path) and attempts > 1:
        log.debug(
            "Failed to retrieve shared secret for {}. Will "
            "attempt up to {} more times".format(service, attempts)
        )
        sleep(1)
        return retrieve_shared_secret(service, attempts=attempts - 1)
    return mapping


def set_new_shared_secret(service):
    """
    Set a new shared secret for the defined service in the
    distributed key value store.
    :param str service: name of the service to create a secret for
    :return dict mapping: the updated config mapping
    """
    log.info(
        "Generating new {} secret. Any other pre-existing older "
        "machines won't be able to authenticate against this new "
        "network. Netsplit might occur.".format(service)
    )
    shared_secret_path = "{}/meshnet/{}/password".format(
        conf().KEY_VALUE_PATH, service
    )
    mapping = try_update_config_mapping({
        shared_secret_path: uuid.uuid4().hex
    })
    return mapping


def ensure_shared_secret(service):
    """
    Ensure a key 'password' exists in the config for a specific meshnet service.
    If no key exists, create it with a new (pseudo) random value
    :param str service: name of the service to ensure a secret for
    :return dict mapping: the updated config mapping
    """
    mapping = retrieve_shared_secret(service)
    shared_secret_path = "{}/meshnet/{}/password".format(
        conf().KEY_VALUE_PATH, service
    )
    if not mapping.get(shared_secret_path):
        mapping = set_new_shared_secret(service)
    return mapping


def update_cjdns_config():
    """
    Ensure a key 'password' exists in the config for the cjdns item in the meshnet config
    If no key exists, create it with a new (pseudo) random value
    :return dict mapping: the updated config mapping
    """
    return ensure_shared_secret('cjdns')


def update_consul_config():
    """
    Ensure a key 'password' exists in the config for the consul item in the meshnet config
    If no key exists, create it with a new (pseudo) random value
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
        'cjdns_port': str(conf().CJDNS_DEFAULT_PORT),
        'cjdns_public_key': cjdns_public_key,
        'cjdns_ipv6_address': cjdns_ipv6_address,
        # todo: get this port dynamically from the cjdroute.conf
        'ssh_port': str(port),
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


@retry(attempts=3, expect=(RuntimeError,))
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
        try:
            bootstrap_host_to_neighbour(
                host, port, connected_host, connected_host_port
            )
        except RuntimeError:
            log.debug(
                "Failed to add new peer to the known host that can ping it. "
                "If a quorum is already established the meshnet reload event we'll "
                "send now should catch it. Skipping for now."
            )
    else:
        log.info(
            "Found no neighbour that could already connect "
            "directly to the new host {}. Sending reload event "
            "and hoping for the best..".format(host)
        )
    send_reload_meshnet()
