from logging import getLogger

from raptiformica.actions.slave import slave_machine
from raptiformica.settings.types import get_first_compute_type, get_first_server_type, \
    retrieve_compute_type_config_for_server_type
from raptiformica.shell.compute import start_instance
from raptiformica.shell.ssh import verify_ssh_agent_running

log = getLogger(__name__)


def retrieve_start_instance_config(server_type=get_first_server_type(), compute_type=get_first_compute_type()):
    """
    Get the source, start instance command and getter commands for the server_type as defined in the compute_type
    :param str compute_type: name of the compute type to start an instance on
    :param str server_type: name of the server type to provision the machine as
    :return tuple start_instance_config: tuple of source, start instance command, get hostname and get port command
    """
    log.debug("Retrieving start instance config")
    compute_type_config_for_server_type = retrieve_compute_type_config_for_server_type(
        server_type=server_type,
        compute_type=compute_type
    )
    source = compute_type_config_for_server_type[
        'source'
    ]
    start_instance_command = compute_type_config_for_server_type[
        'start_instance_command'
    ]
    get_hostname_command = compute_type_config_for_server_type[
        'hostname_get_command'
    ]
    get_port_command = compute_type_config_for_server_type[
        'port_get_command'
    ]
    return source, start_instance_command, get_hostname_command, get_port_command


def start_compute_type(server_type=get_first_server_type(), compute_type=get_first_compute_type()):
    """
    Start a compute instance of type server_type based on the config
    :param str server_type: name of the server type to provision the machine as
    :param str compute_type: name of the compute type to start an instance on
    :return tuple compute_checkout_information: compute_checkout_uuid, host and port
    """
    source, boot_command, hostname_command, port_command = retrieve_start_instance_config(
        server_type=server_type, compute_type=compute_type
    )
    return start_instance(
        server_type, compute_type,
        source, boot_command,
        hostname_command, port_command
    )


def spawn_machine(provision=False, assimilate=False, server_type=get_first_server_type(),
                  compute_type=get_first_compute_type()):
    """
    Start a new instance, provision it and join it into the distributed network
    :param bool provision: whether or not we should assimilate the remote machine
    :param bool assimilate: whether or not we should assimilate the remote machine
    :param str server_type: name of the server type to provision the machine as
    :param str compute_type: name of the compute type to start an instance on
    :return None:
    """
    log.info("Spawning machine of server type {} with compute type {}".format(
        server_type, compute_type
    ))
    verify_ssh_agent_running()
    uuid, host, port = start_compute_type(
        server_type=server_type, compute_type=compute_type
    )
    slave_machine(
        host, port=port,
        assimilate=assimilate,
        provision=provision,
        server_type=server_type,
        uuid=uuid
    )
