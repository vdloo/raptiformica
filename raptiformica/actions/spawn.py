from logging import getLogger

from raptiformica.actions.slave import slave_machine
from raptiformica.settings.load import load_config
from raptiformica.settings.types import get_first_compute_type, get_first_server_type
from raptiformica.shell.compute import start_instance
from raptiformica.shell.ssh import verify_ssh_agent_running

log = getLogger(__name__)


def verify_server_type_implemented_in_compute_type(compute_type_config, server_type):
    """
    Error out when there is no such server type configured for the specified compute type
    :param dict compute_type_config: the compute type config for a specific compute type
    :param str server_type: name of the server type to provision the machine as
    :return None:
    """
    if server_type not in compute_type_config:
        log.error("This compute type has no implementation for server type {}! "
                  "Check your config".format(server_type))
        exit(1)


def retrieve_compute_type_config_for_server_type(server_type=get_first_server_type(),
                                                 compute_type=get_first_compute_type()):
    """
    Load the config for server_type as defined in the config for compute_type
    :param str compute_type: name of the compute type to start an instance on
    :param str server_type: name of the server type to provision the machine as
    :return dict config: the server_type config in the compute_type_config
    """
    config = load_config()
    compute_type_config = config['compute_types'][compute_type]
    verify_server_type_implemented_in_compute_type(
        compute_type_config, server_type
    )
    return compute_type_config[server_type]


def retrieve_start_instance_config(server_type=get_first_server_type(), compute_type=get_first_compute_type()):
    """
    Get the source, start instance command and getter commands for the server_type as defined in the compute_type
    :param str compute_type: name of the compute type to start an instance on
    :param str server_type: name of the server type to provision the machine as
    :return tuple start_instance_config: tuple of source, start instance command, get hostname and get port command
    """
    log.debug("Retrieving instance config")
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
    :return tuple connection_information: host and port
    """
    source, boot_command, hostname_command, port_command = retrieve_start_instance_config(
        server_type=server_type, compute_type=compute_type
    )
    return start_instance(
        compute_type, source, boot_command,
        hostname_command, port_command
    )


def spawn_machine(assimilate=False, server_type=get_first_server_type(), compute_type=get_first_compute_type()):
    """
    :param bool assimilate: whether or not we should assimilate the remote machine
    :param str server_type: name of the server type to provision the machine as
    :param str compute_type: name of the compute type to start an instance on
    :return None:
    """
    log.info("Spawning machine of server type {} with compute type {}".format(
        server_type, compute_type
    ))
    verify_ssh_agent_running()
    host, port = start_compute_type(
        server_type=server_type, compute_type=compute_type
    )
    slave_machine(
        host, port=port, assimilate=assimilate,
        server_type=server_type
    )
