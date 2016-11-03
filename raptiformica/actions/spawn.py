from logging import getLogger

from raptiformica.actions.slave import slave_machine
from raptiformica.settings import KEY_VALUE_PATH
from raptiformica.settings.load import get_config_mapping
from raptiformica.settings.types import get_first_compute_type, get_first_server_type
from raptiformica.shell.compute import start_instance
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
        KEY_VALUE_PATH, compute_type, server_type
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


def spawn_machine(provision=False, assimilate=False, server_type=None, compute_type=None, only_check_available=False):
    """
    Start a new instance, provision it and join it into the distributed network
    :param bool provision: whether or not we should assimilate the remote machine
    :param bool assimilate: whether or not we should assimilate the remote machine
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
        slave_machine(
            host, port=port,
            assimilate=assimilate,
            provision=provision,
            server_type=server_type,
            uuid=uuid
        )
