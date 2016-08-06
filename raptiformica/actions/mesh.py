import os
from logging import getLogger

from operator import itemgetter
from raptiformica.settings import MUTABLE_CONFIG, CJDNS_DEFAULT_PORT
from raptiformica.settings.load import load_config
from raptiformica.shell.execute import run_command_print_ready, raise_failure_factory
from raptiformica.utils import load_json, write_json, ensure_directory

log = getLogger(__name__)

CJDROUTE_CONF_PATH = '/etc/cjdroute.conf'
CONSUL_CONF_PATH = '/etc/consul.d/config.json'


def parse_cjdns_neighbours(meshnet_config):
    """
    Create a dict of entries for connectTo in the cjdroute.conf from the
    meshnet segment of the inherited mutable config
    :param dict meshnet_config: The 'meshnet' part of the inherited mutable config
    :return dict neighbours: a dict of neighbouring machines with as dict-key their
    CJDNS public key.
    """
    neighbours = dict()
    cjdroute_config = load_json(CJDROUTE_CONF_PATH)
    for neighbour in meshnet_config['neighbours'].values():
        host = neighbour['host']
        port = neighbour['port']
        public_key = neighbour['cjdns_public_key']
        if public_key == cjdroute_config['publicKey']:
            continue
        address = "{}:{}".format(host, port)
        neighbours[address] = {
            'password': meshnet_config['cjdns']['password'],
            'publicKey': public_key,
            'peerName': address,
        }
    return neighbours


def configure_cjdroute_conf(config):
    """
    Configure the cjdroute config according to the
    information in the inherited mutable config.
    :param dict config: the mutable config
    :return:
    """
    log.info("Configuring cjdroute config")
    meshnet_config = config['meshnet']
    cjdroute_config = load_json(CJDROUTE_CONF_PATH)
    cjdroute_config['authorizedPasswords'] = [{
        'password': meshnet_config['cjdns']['password']
    }]
    neighbours = parse_cjdns_neighbours(meshnet_config)
    # do not add self as neighbour
    cjdroute_config['interfaces']['UDPInterface'] = [{
        'connectTo': neighbours,
        'bind': '0.0.0.0:{}'.format(CJDNS_DEFAULT_PORT)
    }]
    write_json(cjdroute_config, CJDROUTE_CONF_PATH)


def configure_consul_conf(config):
    """
    Configure the consul config according to the
    information in the inherited mutable config.
    :param dict config: the mutable config
    :return:
    """
    log.info("Configuring consul config")
    cjdroute_config = load_json(CJDROUTE_CONF_PATH)
    consul_config = {
        'bootstrap_expect': 3,
        'data_dir': '/opt/consul',
        'datacenter': 'raptiformica',
        'log_level': 'INFO',
        'node_name': cjdroute_config['ipv6'],
        'server': True,
        'bind_addr': '::',  # todo: bind only to the TUN ipv6 address
        'advertise_addr': cjdroute_config['ipv6'],
        'encrypt': config['meshnet']['consul']['password'],
        'disable_remote_exec': False
    }
    for directory in ('/etc/consul.d', '/etc/opt/consul'):
        ensure_directory(directory)
    write_json(consul_config, CONSUL_CONF_PATH)


def enough_neighbours(config):
    """
    Check if there are enough neighbours to bootstrap or
    join a meshnet. Need a minimum of 3 endpoints to form
    a consensus.
    :param dict config: the mutable config
    :return:
    """
    log.info("Checking if there are enough neighbours to mesh with")
    neighbours = parse_cjdns_neighbours(config['meshnet'])
    enough = len(neighbours) >= 2
    if not enough:
        log.warning("Not enough machines to bootstrap meshnet. "
                    "Need {} more.".format(2 - len(neighbours)))
    elif len(neighbours) == 2:
        log.info("New meshnet will be established")
    return enough


def start_detached_cjdroute():
    """
    Start cjdroute running in the foreground in a detached screen
    Doing it this way because at this point in the process it could be that the remote host does not have an init system
    :return None:
    """
    log.info("Starting cjdroute in the background")
    start_cjdroute_command = "/usr/bin/env screen -d -m bash -c 'cat {} | " \
                             "cjdroute --nobg'".format(CJDROUTE_CONF_PATH)
    run_command_print_ready(
        start_cjdroute_command,
        failure_callback=raise_failure_factory(
            "Failed to start cjdroute in the background"
        ),
        shell=True,
        buffered=False
    )


def start_detached_consul_agent():
    """
    Start the consul agent running in the foreground in a detached screen
    Doing it this way because at this point in the process it could be that the remote host does not have an init system
    :return None:
    """
    log.info("Starting a detached consul agent")
    start_detached_consul_agent_command = "/usr/bin/env screen -d -m /usr/bin/consul agent --config-dir /etc/consul.d/"
    run_command_print_ready(
        start_detached_consul_agent_command,
        failure_callback=raise_failure_factory(
            "Failed to start the consul agent in the background"
        ),
        shell=True,
        buffered=False
    )


def start_meshing_services():
    """
    Start the meshnet services. This enables neighbours to connect
    to this machine.
    :return None:
    """
    log.info("Starting meshing services")
    start_detached_cjdroute()
    start_detached_consul_agent()


def join_meshnet(config):
    """
    Bootstrap or join the distributed network by
    joining consul agents running on the neighbours
    specified in the mutable config
    :param dict config: the mutable config
    :return None:
    """
    log.info("Joining the meshnet")
    neighbours = config['meshnet']['neighbours'].values()
    # todo: poll for consul agent to start instead of stupidly sleeping
    # give the agent some time to start
    consul_join_command = 'sleep 5; consul join '
    for ipv6_address in sorted(map(itemgetter('cjdns_ipv6_address'), neighbours)):
        consul_join_command += '[{}]:8301 '.format(
            ipv6_address
        )
    log.info("running: {}".format(consul_join_command))
    run_command_print_ready(
        consul_join_command,
        failure_callback=raise_failure_factory(
            "Failed to join the configured neighbours"
        ),
        shell=True,
        buffered=False
    )


def mesh_machine():
    """
    Configure the mesh services according to the inherited
    mutable config and start the services. If there are
    enough peers to start or join a meshnet, bootstrap
    or join.
    :return None:
    """
    log.info("Joining the machine into the distributed network")
    config = load_config(MUTABLE_CONFIG)
    configure_cjdroute_conf(config)
    configure_consul_conf(config)
    start_meshing_services()
    # todo: in the future, if there are not enough neighbours to bootstrap
    # the network the running machine should 'boot' faux instances with their
    # own agents. That way there won't be a need for a separate interface to
    # the information derived from consul in the case of less than 3 active
    # machines. Maybe a chroot would be the most compatible way to do something
    # like that.
    if enough_neighbours(config):
        join_meshnet(config)
