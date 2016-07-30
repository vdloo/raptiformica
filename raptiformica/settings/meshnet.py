from logging import getLogger
import uuid

from raptiformica.settings import MUTABLE_CONFIG, CJDNS_DEFAULT_PORT
from raptiformica.settings.load import load_config, write_config
from raptiformica.shell import cjdns

log = getLogger(__name__)


def ensure_shared_secret(config, service):
    shared_secret = config['meshnet'][service].get(
        'password') or uuid.uuid4().hex
    config['meshnet'][service]['password'] = shared_secret
    return config


def update_cjdns_config(config):
    return ensure_shared_secret(config, 'cjdns')


def update_consul_config(config):
    return ensure_shared_secret(config, 'consul')


def update_neighbours_config(config, host, port=22):
    cjdns_public_key = cjdns.get_public_key(host, port=port)
    cjdns_ipv6_address = cjdns.get_ipv6_address(host, port=port)
    config['meshnet']['neighbours'][cjdns_public_key] = {
        'host': host,
        # todo: get this port dynamically from the cjdroute.conf
        'port': CJDNS_DEFAULT_PORT,
        'cjdns_public_key': cjdns_public_key,
        'cjdns_ipv6_address': cjdns_ipv6_address,
    }
    return config


def update_meshnet_config(host, port=22):
    """
    Add a host to the local mutable config
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Updating meshnet config with data from host {}".format(host))
    config = load_config(MUTABLE_CONFIG)
    config = update_cjdns_config(config)
    config = update_consul_config(config)
    config = update_neighbours_config(config, host, port=port)
    write_config(config, MUTABLE_CONFIG)
