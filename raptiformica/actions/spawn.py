from logging import getLogger

from raptiformica.actions.slave import slave_machine, ensure_source_on_machine
from raptiformica.settings import conf
from raptiformica.settings.load import get_config_mapping
from raptiformica.settings.types import get_first_compute_type, get_first_server_type
from raptiformica.shell.cjdns import CJDNS_REPOSITORY
from raptiformica.shell.compute import start_instance
from raptiformica.shell.git import ensure_latest_source_from_artifacts
from raptiformica.shell.hooks import fire_hooks
from raptiformica.shell.ssh import verify_ssh_agent_running
from raptiformica.utils import startswith, endswith

log = getLogger(__name__)


def retrieve_start_instance_config(server_type=None, compute_type=None):
    """
    Get the source, start instance command and getter commands for the server_type as defined in the compute_type
    :param str compute_type: name of the compute type to start an instance on
    :param str server_type: name of the server type to provision the machine as
    :return tuple start_instance_config: tuple of source, start instance command, get hostname and get port command
    """
    log.debug("Retrieving start instance config")
    server_type = server_type or get_first_server_type()
    compute_type = compute_type or get_first_compute_type()
    mapped = get_config_mapping()

    start_instance_path = '{}/compute/{}/{}/'.format(
        conf().KEY_VALUE_PATH, compute_type, server_type
    )
    start_instance_keys = list(filter(
        startswith(start_instance_path),
        mapped
    ))

    def get_first_mapped(item):
        return mapped[next(filter(endswith(item), start_instance_keys))]

    return tuple(map(
        get_first_mapped,
        (
            'source',
            'start_instance',
            'get_hostname',
            'get_port'
        )
    ))


def start_compute_type(server_type=None, compute_type=None):
    """
    Start a compute instance of type server_type based on the config
    :param str server_type: name of the server type to provision the machine as
    :param str compute_type: name of the compute type to start an instance on
    :return tuple compute_checkout_information: compute_checkout_uuid, host and port
    """
    server_type = server_type or get_first_server_type()
    compute_type = compute_type or get_first_compute_type()
    source, boot_command, hostname_command, port_command = retrieve_start_instance_config(
        server_type=server_type, compute_type=compute_type
    )
    return start_instance(
        server_type, compute_type,
        source, boot_command,
        hostname_command, port_command
    )


def cache_repos(server_type=None):
    """
    Cache repos on the client host. When spawning a new machine there is no
    guarantee that another machine has already been spawned and has yielded
    artifacts for reuse. In case of private repos in use they will have to
    be cloned on the client (which presumably has access or a route to the
    location of the repo). Also for repos that will not be transferred back
    to the client host it is nice to only download them once if we can to
    save bandwidth.
    :param str server_type: name of the server type. i.e. headless
    :return None:
    """
    log.info(
        "Caching repos on the client host so the guests "
        "don't have to download them individually"
    )
    ensure_source_on_machine(server_type=server_type, only_cache=True)
    ensure_latest_source_from_artifacts(
        CJDNS_REPOSITORY, "cjdns", only_cache=True
    )


def spawn_machine(provision=False, assimilate=False, after_assimilate=False,
                  after_mesh=False, server_type=None, compute_type=None,
                  only_check_available=False):
    """
    Start a new instance, provision it and join it into the distributed network
    :param bool provision: whether or not we should assimilate the remote machine
    :param bool assimilate: whether or not we should assimilate the remote machine
    :param bool after_assimilate: whether or not we should perform the after
    assimilation hooks
    :param bool after_mesh: Whether or not to perform the after_mesh hooks
    :param str server_type: name of the server type to provision the machine as
    :param str compute_type: name of the compute type to start an instance on
    :param bool only_check_available: Don't really spawn a machine, just check if this host could
    :return None:
    """
    server_type = server_type or get_first_server_type()
    compute_type = compute_type or get_first_compute_type()
    # If we are just checking for availability we are done here
    if not only_check_available:
        log.info(
            "Spawning machine of server type {} with compute "
            "type {}".format(server_type, compute_type)
        )
        verify_ssh_agent_running()
        uuid, host, port = start_compute_type(
            server_type=server_type, compute_type=compute_type
        )
        fire_hooks('after_start_instance')
        # todo: maybe move this caching to slave_machine instead of keeping
        # this only in spawn_machine
        cache_repos(server_type=server_type)
        slave_machine(
            host, port=port,
            assimilate=assimilate,
            after_assimilate=after_assimilate,
            after_mesh=after_mesh,
            provision=provision,
            server_type=server_type,
            uuid=uuid
        )
