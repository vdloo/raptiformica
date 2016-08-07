from logging import getLogger
import uuid

from raptiformica.settings import MUTABLE_CONFIG, CJDNS_DEFAULT_PORT
from raptiformica.settings.load import load_config, write_config
from raptiformica.shell import cjdns

log = getLogger(__name__)


def ensure_shared_secret(config, service):
    """
    Ensure a key 'password' exists in the config for a specific meshnet service.
    If no key exists, create it with a new (psuedo) random value
    :param dict config: the config as found in mutable_config.json
    :param str service: name of the service to ensure a secret for
    :return dict config: the mutated config
    """
    shared_secret = config['meshnet'][service].get(
        'password') or uuid.uuid4().hex
    config['meshnet'][service]['password'] = shared_secret
    return config


def update_cjdns_config(config):
    """
    Ensure a key 'password' exists in the config for the cjdns item in the meshnet config
    If no key exists, create it with a new (psuedo) random value
    :param dict config: the config as found in mutable_config.json
    :return dict config: the mutated config
    """
    return ensure_shared_secret(config, 'cjdns')


def update_consul_config(config):
    """
    Ensure a key 'password' exists in the config for the consul item in the meshnet config
    If no key exists, create it with a new (psuedo) random value
    :param dict config: the config as found in mutable_config.json
    :return dict config: the mutated config
    """
    return ensure_shared_secret(config, 'consul')


def update_neighbours_config(config, host, port=22, uuid=None):
    """
    Update the neighbours config in the mutable_config
    :param dict config: the config as found in mutable_config.json
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str uuid: identifier for a local compute checkout
    :return dict config: the mutated config
    """
    cjdns_public_key = cjdns.get_public_key(host, port=port)
    cjdns_ipv6_address = cjdns.get_ipv6_address(host, port=port)

    neighbour_config = {
        'host': host,
        # todo: get this port dynamically from the cjdroute.conf
        'cjdns_port': CJDNS_DEFAULT_PORT,
        'cjdns_public_key': cjdns_public_key,
        'cjdns_ipv6_address': cjdns_ipv6_address,
        'ssh_port': port,
    }
    if uuid:
        neighbour_config['uuid'] = uuid
    config['meshnet']['neighbours'][cjdns_public_key] = neighbour_config
    return config


def update_meshnet_config(host, port=22, uuid=None):
    """
    Add a host to the local mutable config
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str uuid: identifier for a local compute checkout
    :return None:
    """
    log.info("Updating meshnet config with data from host {}".format(host))
    config = load_config(MUTABLE_CONFIG)
    config = update_cjdns_config(config)
    config = update_consul_config(config)
    config = update_neighbours_config(
        config, host, port=port, uuid=uuid
    )
    write_config(config, MUTABLE_CONFIG)


def ensure_neighbour_removed_from_config(uuid):
    """
    Remove a neighbour from the local mutable_config.json by compute checkout uuid
    :param str uuid: identifier for a local compute checkout
    :return:
    """
    log.debug("Ensuring neighbour with instance checkout uuid {} is "
              "removed from the mutable_config".format(uuid))
    config = load_config(MUTABLE_CONFIG)
    neighbours = {k: v for k, v in config['meshnet']['neighbours'].items()
                  if v['uuid'] != uuid}
    config['meshnet']['neighbours'] = neighbours
    write_config(config, MUTABLE_CONFIG)
