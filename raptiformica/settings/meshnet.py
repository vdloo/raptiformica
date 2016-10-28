import uuid
from os.path import join
from logging import getLogger

from raptiformica.settings import CJDNS_DEFAULT_PORT, KEY_VALUE_PATH
from raptiformica.settings.load import get_config_mapping, try_update_config_mapping
from raptiformica.shell import cjdns

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
        KEY_VALUE_PATH, service
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
        'cjdns_port': CJDNS_DEFAULT_PORT,
        'cjdns_public_key': cjdns_public_key,
        'cjdns_ipv6_address': cjdns_ipv6_address,
        # todo: get this port dynamically from the cjdroute.conf
        'ssh_port': port,
    }
    if uuid:
        neighbour_entry['uuid'] = uuid

    neighbour_path = "{}/meshnet/neighbours/{}/".format(
        KEY_VALUE_PATH, cjdns_public_key
    )
    neighbour_mapping = {
        join(neighbour_path, k): v for k, v in neighbour_entry.items()
    }
    return try_update_config_mapping(neighbour_mapping)


def update_meshnet_config(host, port=22, compute_checkout_uuid=None):
    """
    Add a host to the local mutable config
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

# todo: implement remove neighbour with consul k v API
# def ensure_neighbour_removed_from_config(uuid):
#     """
#     Remove a neighbour from the local mutable_config.json by compute checkout uuid
#     :param str uuid: identifier for a local compute checkout
#     :return:
#     """
#     log.debug("Ensuring neighbour with instance checkout uuid {} is "
#               "removed from the mutable_config".format(uuid))
#     config = load_config(MUTABLE_CONFIG)
#     neighbours = {k: v for k, v in config['meshnet']['neighbours'].items()
#                   if v['uuid'] != uuid}
#     config['meshnet']['neighbours'] = neighbours
#     write_config_mapping(config, MUTABLE_CONFIG)
