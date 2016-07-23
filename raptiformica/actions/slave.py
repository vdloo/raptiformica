from logging import getLogger

from raptiformica.settings.server import get_first_server_type
from raptiformica.shell.config import run_configured_bootstrap_command
from raptiformica.shell.git import ensure_latest_source
from raptiformica.shell.rsync import upload_self
from raptiformica.utils import load_config

log = getLogger(__name__)


def retrieve_provisioning_config(server_type=get_first_server_type()):
    """
    Get the source, name and bootstrap command from the settings for the specified server type
    :param str server_type: name of the server type. i.e. headless
    :return tuple provisioning_config: tuple of source, name and bootstrap command
    """
    log.info("Retrieving provisioning config")
    config = load_config()
    source = config['server_types'][server_type]['source']
    name = config['server_types'][server_type]['name']
    command = config['server_types'][server_type]['bootstrap_command']
    return source, name, command


def provision(host, port=22, server_type=get_first_server_type()):
    """
    Ensure the remote machine is provisioned with the sources from the config file
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str server_type: name of the server type. i.e. headless
    :return None:
    """
    log.info("Provisioning host {} as server type {}".format(host, server_type))
    source, name, command = retrieve_provisioning_config(server_type)
    ensure_latest_source(source, name, host, port=port)
    run_configured_bootstrap_command(command, name, host, port=port)


def slave_machine(host, port=22, assimilate=True, server_type=get_first_server_type()):
    """
    Provision the remote machine and optionally (default yes) assimilate it into the network.
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param bool assimilate: whether or not we should assimilate the remote machine
    :param str server_type: name of the server type to provision the machine as
    :return None:
    """
    upload_self(host, port=port)
    provision(host, port=port, server_type=server_type)
