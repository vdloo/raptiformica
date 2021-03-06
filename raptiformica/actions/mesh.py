import pipes
from socket import gethostname
from collections import OrderedDict
from hashlib import md5
from contextlib import suppress
from multiprocessing.pool import ThreadPool
from time import sleep
from uuid import UUID

from os import remove
from os.path import join, isfile
from logging import getLogger
from random import shuffle
from shutil import rmtree
from os import path

from raptiformica.settings import conf
from raptiformica.settings.load import get_config_mapping
from raptiformica.settings.meshnet import update_neighbours_config
from raptiformica.shell.execute import run_command_print_ready, run_command, check_nonzero_exit, \
    log_failure_factory, raise_failure_factory
from raptiformica.shell.hooks import fire_hooks
from raptiformica.utils import load_json, write_json, ensure_directory, startswith, wait, group_n_elements, \
    calculate_checksum, retry, calculate_lines_checksum

log = getLogger(__name__)

CJDROUTE_CONF_PATH = '/etc/cjdroute.conf'
CJDROUTE_CONF_HASH = '/var/run/cjdroute_config_hash'
CONSUL_CONF_PATH = '/etc/consul.d/config.json'
CONSUL_CONF_HASH = '/var/run/consul_config_hash'
CONSUL_JOIN_BATCH_SIZE = 1
CONSUL_JOIN_TIMEOUT = 60
WAIT_FOR_VIRTUAL_NETWORK_ADAPTER_TIMEOUT = 15
WAIT_FOR_CONSUL_PORT_TIMEOUT = 15
WAIT_FOR_CJDROUTE_PORT_TIMEOUT = 15
WAIT_FOR_CONSUL_TIMEOUT = 15
CONSUL_STATE_DIRS = ['/opt/consul']


class ConsulSharedSecretChanged(RuntimeError):
    pass


def list_neighbours(mapping):
    """
    List all cjdns neighbours by public key
    :param dict mapping: the config mapping to parse the neighbours from
    :return iter[str, ..]: public keys of all neighbours in the config
    """
    neighbours_path = "{}/meshnet/neighbours/".format(conf().KEY_VALUE_PATH)
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
    return mapping["{}/meshnet/cjdns/password".format(conf().KEY_VALUE_PATH)]


def get_consul_password(mapping):
    """
    Retrieve the consul password from the config mapping
    :param dict mapping: the config mapping to get the shared secret from
    :return str secret: the shared consul secret
    """
    return mapping["{}/meshnet/consul/password".format(conf().KEY_VALUE_PATH)]


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
        conf().KEY_VALUE_PATH
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


@retry(attempts=2, expect=(ValueError,))
def configure_cjdroute_conf():
    """
    Configure the cjdroute config according to the
    information in the retrieved mutable config.
    :return:
    """
    log.info("Configuring cjdroute config")

    mapping = get_config_mapping()
    cjdns_secret = get_cjdns_password(mapping)
    cjdroute_config = OrderedDict(load_json(CJDROUTE_CONF_PATH))
    cjdroute_config['authorizedPasswords'] = [{
        'password': cjdns_secret,
    }]
    neighbours = parse_cjdns_neighbours(mapping)
    neighbour_items = list(neighbours.items())
    # A python3 dict is non-deterministic but not random
    shuffle(neighbour_items)
    shuffled_neighbours = OrderedDict(neighbour_items)
    cjdroute_config['interfaces']['UDPInterface'] = [{
        'connectTo': shuffled_neighbours,
        'bind': '0.0.0.0:{}'.format(conf().CJDNS_DEFAULT_PORT)
    }]
    cjdroute_config['interfaces']['ETHInterface'] = [{
        # Disable peer auto-discovery
        'beacon': 0,
        'bind': 'all',
        'connectTo': {}
    }]
    write_json(cjdroute_config, CJDROUTE_CONF_PATH, sort_keys=False)


def configure_consul_conf():
    """
    Configure the consul config according to the
    information in the inherited mutable config.
    :return:
    """
    log.info("Configuring consul config")
    cjdroute_config = load_json(CJDROUTE_CONF_PATH)
    cluster_change_handler = "bash -c \"" \
                             "cd '{}'; " \
                             "export PYTHONPATH=.; " \
                             "./bin/raptiformica_hook.py cluster_change " \
                             "--verbose\"".format(conf().RAPTIFORMICA_DIR)
    shared_secret = get_consul_password(get_config_mapping())
    node_id = str(
        UUID(bytes=md5(str.encode(cjdroute_config['ipv6'])).digest())
    )
    consul_config = {
        'bootstrap_expect': 3,
        'data_dir': '/opt/consul',
        'datacenter': 'raptiformica',
        'log_level': 'INFO',
        'node_name': gethostname(),
        # deterministic node ID derived from the IPv6 address
        'node_id': node_id,
        'server': True,
        'bind_addr': '::',  # todo: bind only to the TUN ipv6 address
        'advertise_addr': cjdroute_config['ipv6'],
        'encrypt': shared_secret,
        'disable_remote_exec': True,
        'enable_script_checks': True,
        'performance': {
            # High performance settings. Machines leave and join the
            # cluster fast and often.
            'raft_multiplier': 10
        },
        'dns_config': {
            'allow_stale': True,
            "recursor_timeout": '1s'
        },
        "leave_on_terminate": True,
        "skip_leave_on_interrupt": False,
        "disable_update_check": True,
        "reconnect_timeout": "8h",  # The value must be >= 8 hours.
        "reconnect_timeout_wan": "8h",
        "translate_wan_addrs": False,
        "rejoin_after_leave": True,
        'watches': [
            {
                'type': 'service',
                'service': 'consul',
                'handler': cluster_change_handler
            },
            {
                'type': 'event',
                'name': 'notify_cluster_change',
                'handler': cluster_change_handler
            },
        ]
    }
    for directory in ('/etc/consul.d', '/etc/opt/consul'):
        ensure_directory(directory)
    write_json(consul_config, CONSUL_CONF_PATH)


def configure_raptiformica_conf():
    """
    Place start on boot configurations for the agent
    :return None:
    """
    log.info(
        "Configuring the agent to run at "
        "boot (if the system supports that)"
    )

    servicefiles_path = '/usr/lib/systemd/system/'
    servicefile_path = '{}/raptiformica.service'.format(servicefiles_path)
    if not path.exists(servicefiles_path):
        return

    start_detached_agent_command = "/usr/bin/env screen -d -m sh -c '" \
                                   "PYTHONPATH=/usr/etc/raptiformica " \
                                   "python3 /usr/etc/raptiformica/bin/" \
                                   "raptiformica_agent.py'"
    enable_commands = [] if path.exists(servicefile_path) else [
        'systemctl daemon-reload',
        'systemctl enable raptiformica'
    ]

    unit_content = """[Unit]
Description=Start raptiformica agent

[Service]
Type=oneshot
ExecStart={}
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
""".format(start_detached_agent_command)
    with open(servicefile_path, 'w+') as f:
        f.write(unit_content)

    for enable_command in enable_commands:
        run_command_print_ready(enable_command, shell=True, buffered=False)


def count_neighbours():
    """
    Count the amount of peers in the distributed network
    :return:
    """
    mapping = get_config_mapping()
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


def stop_detached_cjdroute():
    """
    Stop any possible already running cjdroute processes.
    :return:
    """
    log.info("Stopping cjdroute in the background")
    kill_running = "ps aux | grep [c]jdroute | awk '{print $2}' | " \
                   "xargs --no-run-if-empty -I {} " \
                   "sh -c \"grep -q docker /proc/{}/cgroup && " \
                   "! grep -q name=systemd:/docker /proc/1/cgroup || kill {}\""
    run_command_print_ready(
        kill_running,
        shell=True,
        buffered=False
    )


def check_if_port_available_factory(port):
    """
    Create a function that checks if the specified port is in use
    :param int port: The port to check
    :return func check_if_port_available: function that checks if
    the port is in use
    """
    def check_if_port_available():
        """
        Check if a port is in use
        :return bool not_in_use: True if not in use, False if in use
        """
        check_port_command = "netstat -tuna | grep -E \"{:d}\s\"".format(port)
        return not check_nonzero_exit(check_port_command)
    return check_if_port_available


def block_until_cjdroute_port_is_free():
    """
    Wait for the cjdroute port to become available. If it
    was in use before it could take a while before the OS
    frees it for use.
    :return None:
    """
    log.info("Waiting until the cjdroute port becomes available")
    wait(
        check_if_port_available_factory(conf().CJDNS_DEFAULT_PORT),
        timeout=WAIT_FOR_CJDROUTE_PORT_TIMEOUT
    )


def ensure_ipv6_enabled():
    """
    Ensure IPv6 is enabled at the kernel level, otherwise cjdroute
    will fail with a cryptic error like:

    Got error [Failed to configure tunnel [NetPlatform_linux.c:153
    ioctl(SIOCSIFADDR) [Permission denied]]]

    If the command fails, the raptiformica will continue and try anyway

    :return None:
    """
    log.info("Ensuring IPv6 is enabled at the kernel level")
    ensure_ipv6_command = "/usr/bin/env sysctl net.ipv6.conf.all.disable_ipv6=0"
    run_command_print_ready(
        ensure_ipv6_command,
        failure_callback=log_failure_factory(
            "Failed to ensure IPv6 was enabled at the kernel level. Assuming OK. "
            "If not, cjdroute will later fail to configure the tunnel."
        ),
        shell=True,
        buffered=False
    )


def start_detached_cjdroute():
    """
    Start cjdroute running in the foreground in a detached screen
    Doing it this way because at this point in the process it could
    be that the remote host does not have an init system
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
    log.info("Waiting until virtual network adapter becomes available")
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
    Doing it this way because at this point in the process it could be that
    the remote host does not have an init system
    :return None:
    """
    log.info("Starting a detached consul agent")
    start_detached_consul_agent_command = "/usr/bin/env screen -d -m " \
                                          "/usr/bin/consul agent " \
                                          "-config-dir /etc/consul.d/ " \
                                          "-ui"
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


def cjdroute_config_hash_outdated():
    """
    Check the current cjdroute config hash against the config hash written
    to /var/run when the last cjdroute instance was started.
    If it is outdated it means we are allowing all neighbours to connect
    and that we still allow stale IP addresses of previous neighbours to connect.
    :return None:
    """
    log.info(
        "Checking if the latest reported running "
        "cjdroute config is still up to date"
    )
    config_hash_file_exists = isfile(CJDROUTE_CONF_HASH)
    if config_hash_file_exists:
        with open(CJDROUTE_CONF_HASH, 'rb') as config_hash_file:
            binary_stored_hash = config_hash_file.read()
            stored_hash = binary_stored_hash.decode('utf-8')
        return stored_hash != calculate_lines_checksum(CJDROUTE_CONF_PATH)
    else:
        # There is no config hash yet so it is not up to
        # date because it does not exist
        return True


def write_cjdroute_config_hash():
    """
    Write a hash of the current cjdroute config to /var/run
    so we can later check if the running cjdroute is still up to date.
    If that is the case then we don't have to restart cjdns.
    :return None:
    """
    log.info(
        "Writing hash of current cjdroute config so "
        "we can only reload when we have to"
    )
    with open(CJDROUTE_CONF_HASH, 'wb') as config_hash_file:
        config_hash = calculate_lines_checksum(CJDROUTE_CONF_PATH)
        binary_config_hash = config_hash.encode('utf-8')
        config_hash_file.write(binary_config_hash)


@retry(attempts=5, expect=(TimeoutError,))
def ensure_cjdns_routing():
    """
    Start a new cjdroute instance, wait until the distributed
    network is available and ensure the routes
    :return:
    """
    log.info("Ensuring cjdns routing")
    if cjdroute_config_hash_outdated() or not check_if_tun0_is_available():
        stop_detached_cjdroute()
        block_until_cjdroute_port_is_free()
        ensure_ipv6_enabled()
        start_detached_cjdroute()
        write_cjdroute_config_hash()
        block_until_tun0_becomes_available()
        ensure_ipv6_routing()


def ensure_no_consul_running():
    """
    Kill any consul processes
    :return None:
    """
    log.info("Stopping any running consul processes")
    kill_running = "ps aux | grep [c]onsul | awk '{print $2}' | " \
                   "xargs --no-run-if-empty -I {} " \
                   "sh -c \"grep -q docker /proc/{}/cgroup && " \
                   "! grep -q name=systemd:/docker /proc/1/cgroup || kill -2 {}\""  # SIGINT
    run_command_print_ready(
        kill_running,
        shell=True,
        buffered=False
    )


def clean_up_old_consul_data():
    """
    Clean up old peer state (raft db and serf data)
    :return None:
    """
    log.info("Ensuring /opt/consul is nonexistent")
    rmtree('/opt/consul', ignore_errors=True)


def clean_up_old_consul():
    """
    Clean up any lingering consul processes and data
    :return None:
    """
    log.info("Cleaning up any old consul processes and data")
    ensure_no_consul_running()
    clean_up_old_consul_data()


def reload_consul_agent():
    """
    Reload the consul configuration.
    This is the same as sending a SIGHUP to the consul process
    :return None:
    """
    log.info("Reloading the consul agent")
    reload_agent = "consul reload"
    run_command_print_ready(
        reload_agent,
        shell=True,
        buffered=False
    )


def consul_config_hash_outdated():
    """
    Check the current consul config hash against the config hash written
    to /var/run when the last consul agent was started.
    :return bool outdated: True if outdated, False if up to date
    """
    log.info(
        "Checking if the latest reported running "
        "consul config is used by the agent"
    )
    config_hash_file_exists = isfile(CONSUL_CONF_HASH)
    if config_hash_file_exists:
        with open(CONSUL_CONF_HASH, 'rb') as config_hash_file:
            binary_stored_hash = config_hash_file.read()
            stored_hash = binary_stored_hash.decode('utf-8')
        return stored_hash != calculate_checksum(CONSUL_CONF_PATH)
    else:
        # There is no config hash yet so it is not up to
        # date because it does not exist
        return True


def consul_keyring_in_memory_is_stale(shared_secret):
    """
    Check the shared secret from the config against the one in
    the local keyring in memory
    :param str shared_secret: The up to date shared secret
    :return bool changed: True if changed, False if up to date
    """
    log.info(
        "Checking if the keyring in memory is up to "
        "date with the shared secret from the config"
    )
    check_shared_secret_up_to_date = "if consul keyring -list > /dev/null; " \
                                     "then consul keyring -list | " \
                                     "grep -q {}; else /bin/true; fi" \
                                     "".format(pipes.quote(shared_secret))
    return not check_nonzero_exit(check_shared_secret_up_to_date)


def consul_keyring_on_disk_is_stale(shared_secret):
    """
    Check the shared secret from the config against the one in
    the local keyring on disk
    :param str shared_secret: The up to date shared secret
    :return bool changed: True if changed, False if up to date
    """
    log.info(
        "Checking if the keyring on disk is up to "
        "date with the shared secret from the config"
    )
    check_shared_secret_up_to_date = "grep {} /opt/consul/serf/local.keyring" \
                                     "".format(pipes.quote(shared_secret))
    return not check_nonzero_exit(check_shared_secret_up_to_date)


def consul_shared_secret_changed():
    """
    Check the shared secret from the config against the one in
    the local keyring on disk and in memory
    :return bool changed: True if changed, False if up to date
    """
    log.info("Checking if we should update the consul shared secret")
    shared_secret = get_consul_password(get_config_mapping())
    return consul_keyring_on_disk_is_stale(
        shared_secret
    ) or consul_keyring_in_memory_is_stale(
        shared_secret
    )


@retry(attempts=15, expect=(ConsulSharedSecretChanged,))
def raise_if_shared_secret_changed():
    """
    Raise exception if the consul shared secret changed.
    Checks a couple of times over a couple of seconds.
    At any positive result this function will assume OK
    to dampen ripples in a sufficiently large cluster.
    :return None:
    """
    if consul_shared_secret_changed():
        sleep(1)
        raise ConsulSharedSecretChanged(
            "The consul shared secret might have become stale"
        )


def write_consul_config_hash():
    """
    Write a hash of the current consul config to /var/run
    so we can later check if the running consul agent is still up to date.
    If that is the case then we don't have to reload the consul agent.
    :return None:
    """
    log.info(
        "Writing hash of current consul config so "
        "we can only reload when we have to"
    )
    with open(CONSUL_CONF_HASH, 'wb') as config_hash_file:
        config_hash = calculate_checksum(CONSUL_CONF_PATH)
        binary_config_hash = config_hash.encode('utf-8')
        config_hash_file.write(binary_config_hash)


def remove_old_consul_keyring():
    """
    Remove any old local consul keyring. Can be removed when
    https://github.com/hashicorp/consul/issues/719 is fixed.
    The configured shared secret will not be used if the local
    keyring already exists because it takes precedence over the
    configuration options
    :return None:
    """
    with suppress(FileNotFoundError):
        remove('/opt/consul/serf/local.keyring')


def consul_outage_detected():
    """
    Check if consul reports an outage. If so, we need to automatically resolve it.
    See: https://www.consul.io/docs/guides/outage.html
    :return bool outage: True if no leader can be elected.
    """
    log.debug("Checking if the local consul agent reports an outage state")
    command = ['consul', 'kv', 'get', '/raptiformica/raptiformica_api_version']
    _, _, standard_error = run_command(
        command, timeout=WAIT_FOR_CONSUL_TIMEOUT
    )
    return standard_error and "Unexpected response code: 500" in standard_error


def remove_consul_local_state():
    """
    Remove all local consul state. If there was a consul outage some data might
    now be lost. That should be OK because the consensus is best effort and any
    state stored in the distributed key value store should be commutative and
    persisted on disk periodically. Once a new quorum has been established the
    state from disk will be pushed to the kv store once again. Any other nodes
    with other local data will push (over) the same store until an equilibrium
    has been reached.
    :return None:
    """
    for path_to_clean in CONSUL_STATE_DIRS:
        rmtree(path_to_clean, ignore_errors=True)


def flush_consul_agent_if_necessary():
    """
    Flush consul if the agent reports that there is no leader
    since it was last (re)started or reloaded
    :return None:
    """
    if enough_neighbours() and consul_outage_detected():
        log.info(
            "Consul outage detected. Removing local state "
            "to re-establish a fresh quorum. Data loss imminent."
        )
        remove_consul_local_state()


def restart_consul_agent_if_necessary():
    """
    Restart consul if the shared secret has changed.
    :return None:
    """
    try:
        raise_if_shared_secret_changed()
    except ConsulSharedSecretChanged:
        remove_old_consul_keyring()
        restart_consul()


def reload_consul_agent_if_necessary():
    """
    Reload consul if the agent is running but the config file has changed
    since it was last (re)started or reloaded
    :return None:
    """
    if consul_config_hash_outdated():
        remove_old_consul_keyring()
        reload_consul_agent()
        write_consul_config_hash()


def restart_consul():
    """
    Stop and start the consul agent. If the agent is not
    already running, just start it.
    :return None:
    """
    clean_up_old_consul()
    start_detached_consul_agent()
    write_consul_config_hash()


@retry(attempts=5, expect=(TimeoutError,))
def ensure_consul_agent():
    """
    Ensure the consul agent is running with the latest configuration
    SIGHUP (reload) if already running. If not already running, start
    the agent. Blocks until the agent becomes available.
    :return None:
    """
    log.info("Ensuring consul agent is running with an up to date configuration")
    flush_consul_agent_if_necessary()
    consul_running = check_if_consul_is_available()
    if consul_running:
        restart_consul_agent_if_necessary()
        reload_consul_agent_if_necessary()
    else:
        restart_consul()
    block_until_consul_becomes_available()


def ensure_raptiformica_agent():
    """
    Ensure the raptiformica agent is running. Will attempt to rejoin
    the configured network if the machine has lost connection to the
    cluster.

    Starts the raptiformica agent running in the foreground in a
    detached screen. Doing it this way because it could be that the
    remote host does not have an init system. Subshell exits zero but
    does not run in case another agent is already running.
    :return None:
    """
    log.info("Ensuring raptiformica agent is running")
    start_detached_agent_command = "/usr/bin/env screen -d -m sh -c '" \
                                   "PYTHONPATH=/usr/etc/raptiformica " \
                                   "python3 /usr/etc/raptiformica/bin/" \
                                   "raptiformica_agent.py'"
    run_command_print_ready(
        start_detached_agent_command,
        failure_callback=raise_failure_factory(
            "Failed to start the raptiformica agent in the background"
        ),
        shell=True,
        buffered=False
    )


def configure_meshing_services():
    """
    Configures the meshnet services.
    :return None:
    """
    log.info("Configuring the meshnet services")
    configure_cjdroute_conf()
    configure_consul_conf()
    configure_raptiformica_conf()


def start_meshing_services():
    """
    Start the meshnet services. This enables neighbours to connect
    to this machine.
    :return None:
    """
    log.info("Starting meshing services")
    ensure_raptiformica_agent()
    ensure_cjdns_routing()
    ensure_consul_agent()


def get_neighbour_hosts(mapping):
    """
    Return a list of all known neighbour hosts
    :param dict mapping: Key value mapping with the config data
    :return list ipv6_addresses: All known neighbour hosts
    """
    neighbours_path = "{}/meshnet/neighbours/".format(conf().KEY_VALUE_PATH)
    public_keys = list_neighbours(mapping)
    ipv6_addresses = list()
    for pk in public_keys:
        neighbour_path = join(neighbours_path, pk)
        ipv6_addresses.append(
            mapping[join(neighbour_path, 'cjdns_ipv6_address')]
        )
    return ipv6_addresses


def run_consul_join(ipv6_addresses):
    """
    Consul join all specified ipv6 addresses.
    :param list ipv6_addresses: Known neighbour hosts
    :return None:
    """
    consul_join_command = 'consul join '
    for ipv6_address in sorted(ipv6_addresses):
        consul_join_command += '[{}]:8301 '.format(
            ipv6_address
        )
    log.info("running: {}".format(consul_join_command))
    run_command_print_ready(
        consul_join_command,
        failure_callback=raise_failure_factory(
            "Failed to join the configured "
            "neighbours {}".format(ipv6_addresses)
        ),
        shell=True,
        buffered=False,
        timeout=CONSUL_JOIN_TIMEOUT
    )


@retry(attempts=3, expect=(RuntimeError,))
def try_run_consul_join(ipv6_addresses):
    """
    Try and soft fail joining all specified ipv6 addresses.
    :param list ipv6_addresses: Known neighbour hosts
    :return None:
    """
    return run_consul_join(ipv6_addresses=ipv6_addresses)


def not_already_known_consul_neighbour(ipv6_address):
    """
    Check if the ipv6 address is not already in the members list
    for the running agent
    :param str ipv6_address: The ipv6 address to check
    :return bool not_yet_already_known: True if not yet known,
    False if already in the list
    """
    log.info(
        "Checking if the consul agent already knows {}".format(ipv6_address)
    )
    check_already_known = "consul members | grep -v left | " \
                          "grep {}".format(ipv6_address)
    return not check_nonzero_exit(check_already_known)


def join_consul_neighbours(mapping):
    """
    Consul join all known neighbours. Will join as many instances at
    the same time as threads in the threadpool.
    :param dict mapping: Key value mapping with the config data
    :return None:
    """
    ipv6_addresses = get_neighbour_hosts(mapping)
    shuffle(ipv6_addresses)
    new_ipv6_addresses = list(
        filter(not_already_known_consul_neighbour, ipv6_addresses)
    )
    pool = ThreadPool()
    groups = group_n_elements(
        new_ipv6_addresses, CONSUL_JOIN_BATCH_SIZE
    )
    for ipv6_addresses in groups:
        pool.apply_async(try_run_consul_join, args=(ipv6_addresses,))
    pool.close()
    pool.join()


def join_meshnet():
    """
    Bootstrap or join the distributed network by contacting the neighbours
    specified in the mutable config
    :return None:
    """
    log.info("Joining the meshnet")
    mapping = get_config_mapping()
    join_consul_neighbours(mapping)


def attempt_join_meshnet():
    """
    Configure the mesh services according to the inherited
    mutable config and start the services. If there are
    enough peers to start or join a meshnet, bootstrap
    or join.
    :return None:
    """
    log.info("Joining the machine into the distributed network")
    update_neighbours_config(remove=False)
    configure_meshing_services()
    start_meshing_services()
    # todo: in the future, if there are not enough neighbours to bootstrap
    # the network the running machine should 'boot' faux instances with their
    # own agents. That way there won't be a need for a separate interface to
    # the information derived from consul in the case of less than 3 active
    # machines. Maybe a chroot would be the most compatible way to do something
    # like that.
    if enough_neighbours():
        join_meshnet()


def mesh_machine(after_mesh=True):
    """
    Configure the mesh services and attempt to join the meshnet.
    If there are 'after_mesh' hooks configured, fire those.
    Exit the process with exit code 0 if no exception occurred
    so that the remote raptiformica command caller registers
    the execution as successful.
    :param bool after_mesh: Whether or not to perform the after_mesh hooks
    :return None:
    """
    attempt_join_meshnet()
    if after_mesh:
        fire_hooks('after_mesh')
