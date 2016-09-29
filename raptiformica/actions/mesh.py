from os.path import join
from logging import getLogger

from raptiformica.settings import CJDNS_DEFAULT_PORT, RAPTIFORMICA_DIR, KEY_VALUE_PATH
from raptiformica.settings.load import get_config
from raptiformica.shell.execute import run_command_print_ready, raise_failure_factory, run_command, check_nonzero_exit
from raptiformica.shell.hooks import fire_hooks
from raptiformica.utils import load_json, write_json, ensure_directory, startswith, wait

log = getLogger(__name__)

CJDROUTE_CONF_PATH = '/etc/cjdroute.conf'
CONSUL_CONF_PATH = '/etc/consul.d/config.json'
WAIT_FOR_VIRTUAL_NETWORK_ADAPTER_TIMEOUT = 10
WAIT_FOR_CONSUL_TIMEOUT = 10


def list_neighbours(mapping):
    """
    List all cjdns neighbours by public key
    :param dict mapping: the config mapping to parse the neighbours from
    :return iter[str, ..]: public keys of all neighbours in the config
    """
    neighbours_path = "{}/meshnet/neighbours/".format(KEY_VALUE_PATH)
    public_keys = set(map(
        lambda p: p.replace(neighbours_path, '').split('/')[0],
        filter(
            startswith(neighbours_path),
            mapping
        )
    ))
    return public_keys


def get_cjdns_password(mapping):
    """
    Retrieve the cjdns password from the config mapping
    :param dict mapping: the config mapping to get the shared secret from
    :return str secret: the shared cjdns secret
    """
    return mapping["{}/meshnet/cjdns/password".format(KEY_VALUE_PATH)]


def get_consul_password(mapping):
    """
    Retrieve the consul password from the config mapping
    :param dict mapping: the config mapping to get the shared secret from
    :return str secret: the shared consul secret
    """
    return mapping["{}/meshnet/consul/password".format(KEY_VALUE_PATH)]


def parse_cjdns_neighbours(mapping):
    """
    Create a dict of entries for connectTo in the cjdroute.conf from the
    meshnet segment of the distributed k v config mapping
    :param dict mapping: the config mapping to parse the neighbours from
    :return dict neighbours: a dict of neighbouring machines with as dict-key their
    CJDNS public key.
    """
    neighbours = dict()

    cjdroute_config = load_json(CJDROUTE_CONF_PATH)
    local_public_key = cjdroute_config['publicKey']

    neighbours_path = "{}/meshnet/neighbours/".format(
        KEY_VALUE_PATH
    )
    public_keys = list_neighbours(mapping)
    for pk in public_keys:
        if pk == local_public_key:
            continue
        neighbour_path = join(neighbours_path, pk)
        password = get_cjdns_password(mapping)
        host = mapping[join(neighbour_path, 'host')]
        cjdns_port = mapping[join(neighbour_path, 'cjdns_port')]
        address = "{}:{}".format(host, cjdns_port)
        neighbours[address] = {
            'password': password,
            'publicKey': pk,
            'peerName': address
        }
    return neighbours


def configure_cjdroute_conf():
    """
    Configure the cjdroute config according to the
    information in the retrieved mutable config.
    :return:
    """
    log.info("Configuring cjdroute config")

    mapping = get_config()
    cjdns_secret = get_cjdns_password(mapping)
    cjdroute_config = load_json(CJDROUTE_CONF_PATH)
    cjdroute_config['authorizedPasswords'] = [{
        'password': cjdns_secret,
    }]
    neighbours = parse_cjdns_neighbours(mapping)
    cjdroute_config['interfaces']['UDPInterface'] = [{
        'connectTo': neighbours,
        'bind': '0.0.0.0:{}'.format(CJDNS_DEFAULT_PORT)
    }]
    write_json(cjdroute_config, CJDROUTE_CONF_PATH)


def configure_consul_conf():
    """
    Configure the consul config according to the
    information in the inherited mutable config.
    :param dict config: the mutable config
    :return:
    """
    log.info("Configuring consul config")
    cjdroute_config = load_json(CJDROUTE_CONF_PATH)
    cluster_change_handler = "bash -c \"" \
                             "cd '{}'; " \
                             "export PYTHONPATH=.; " \
                             "./bin/raptiformica_hook.py cluster_change " \
                             "--verbose\"".format(RAPTIFORMICA_DIR)
    shared_secret = get_consul_password(get_config())
    consul_config = {
        'bootstrap_expect': 3,
        'data_dir': '/opt/consul',
        'datacenter': 'raptiformica',
        'log_level': 'INFO',
        'node_name': cjdroute_config['ipv6'],
        'server': True,
        'bind_addr': '::',  # todo: bind only to the TUN ipv6 address
        'advertise_addr': cjdroute_config['ipv6'],
        'encrypt': shared_secret,
        'disable_remote_exec': False,
        'watches': [
            {
                'type': 'service',
                'service': 'consul',
                'handler': cluster_change_handler
            }
        ]
    }
    for directory in ('/etc/consul.d', '/etc/opt/consul'):
        ensure_directory(directory)
    write_json(consul_config, CONSUL_CONF_PATH)


def count_neighbours():
    """
    Count the amount of peers in the distributed network
    :return:
    """
    mapping = get_config()
    cjdroute_config = load_json(CJDROUTE_CONF_PATH)
    local_public_key = cjdroute_config['publicKey']
    return len([pk for pk in list_neighbours(mapping) if pk != local_public_key])


def enough_neighbours():
    """
    Check if there are enough neighbours to bootstrap or
    join a meshnet. Need a minimum of 3 endpoints to form
    a consensus.
    :return:
    """
    log.info("Checking if there are enough neighbours to mesh with")
    amount = count_neighbours()

    enough = amount >= 2
    if not enough:
        log.warning("Not enough machines to bootstrap meshnet. "
                    "Need {} more.".format(2 - amount))
    elif amount == 2:
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


def check_if_tun0_is_available():
    """
    Check if the virtual network adapter is available
    :return bool available: True or False based on whether the tun0 devices is available
    """
    check_interface_command = "ip addr show tun0"
    return check_nonzero_exit(check_interface_command)


def block_until_tun0_becomes_available():
    """
    Poll the network interfaces list until the virtual network adapter becomes available
    :return None || TimeoutError:
    """
    log.info("Waiting until virtual network adapter becomes availble")
    wait(
        check_if_tun0_is_available,
        timeout=WAIT_FOR_VIRTUAL_NETWORK_ADAPTER_TIMEOUT
    )


def ensure_ipv6_routing():
    """
    Ensure there are entries in the routing-table that point to the tun adapter
    This needs to happen after cjdroute starts because only then tun0 exists.
    :return:
    """
    log.info("Ensuring there is a route to the TUN adapter")
    routing_rules = (
        'fe80::/64 dev eth0  proto kernel  metric 256  pref medium',
        'fc00::/8 dev tun0  proto kernel  metric 256  mtu 1304 pref medium'
    )
    for rule in routing_rules:
        run_command(
            "ip -6 route add {}".format(rule), shell=True,
        )


def start_detached_consul_agent():
    """
    Start the consul agent running in the foreground in a detached screen
    Doing it this way because at this point in the process it could be that the remote host does not have an init system
    :return None:
    """
    log.info("Starting a detached consul agent")
    start_detached_consul_agent_command = "/usr/bin/env screen -d -m " \
                                          "/usr/bin/consul agent " \
                                          "-config-dir /etc/consul.d/ " \
                                          "-ui-dir /usr/etc/consul_web_ui"
    run_command_print_ready(
        start_detached_consul_agent_command,
        failure_callback=raise_failure_factory(
            "Failed to start the consul agent in the background"
        ),
        shell=True,
        buffered=False
    )


def check_if_consul_is_available():
    """
    Check if consul is available
    :return bool available: True or False based on whether consul is available
    """
    # If we can run 'consul members' with a nonzero exit code
    # we can be sure that the agent is ready for interaction
    check_consul_available_command = "consul members"
    return check_nonzero_exit(check_consul_available_command)


def block_until_consul_becomes_available():
    """
    Poll the consul API by running 'members' until it responds nonzero
    :return None || TimeoutError:
    """
    log.info("Waiting until consul becomes available")
    wait(
        check_if_consul_is_available,
        timeout=WAIT_FOR_CONSUL_TIMEOUT
    )


def start_meshing_services():
    """
    Start the meshnet services. This enables neighbours to connect
    to this machine.
    :return None:
    """
    log.info("Starting meshing services")
    start_detached_cjdroute()
    block_until_tun0_becomes_available()
    ensure_ipv6_routing()
    start_detached_consul_agent()
    block_until_consul_becomes_available()


def join_meshnet():
    """
    Bootstrap or join the distributed network by
    joining consul agents running on the neighbours
    specified in the mutable config
    :return None:
    """
    log.info("Joining the meshnet")
    mapping = get_config()
    neighbours_path = "{}/meshnet/neighbours/".format(KEY_VALUE_PATH)
    public_keys = list_neighbours(mapping)
    ipv6_addresses = list()
    for pk in public_keys:
        neighbour_path = join(neighbours_path, pk)
        ipv6_addresses.append(
            mapping[join(neighbour_path, 'cjdns_ipv6_address')]
        )

    # todo: poll for consul agent to start instead of stupidly sleeping
    # give the agent some time to start
    consul_join_command = 'consul join '
    for ipv6_address in sorted(ipv6_addresses):
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


def attempt_join_meshnet():
    """
    Configure the mesh services according to the inherited
    mutable config and start the services. If there are
    enough peers to start or join a meshnet, bootstrap
    or join.
    :return None:
    """
    log.info("Joining the machine into the distributed network")
    configure_cjdroute_conf()
    configure_consul_conf()
    start_meshing_services()
    # todo: in the future, if there are not enough neighbours to bootstrap
    # the network the running machine should 'boot' faux instances with their
    # own agents. That way there won't be a need for a separate interface to
    # the information derived from consul in the case of less than 3 active
    # machines. Maybe a chroot would be the most compatible way to do something
    # like that.
    if enough_neighbours():
        join_meshnet()


def mesh_machine():
    """
    Configure the mesh services and attempt to join the meshnet.
    If there are 'after_mesh' hooks configured, fire those.
    Exit the process with exit code 0 if no exception occurred
    so that the remote raptiformica command caller registers
    the execution as successful.
    :return None:
    """
    attempt_join_meshnet()
    fire_hooks('after_mesh')
