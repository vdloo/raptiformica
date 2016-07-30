from logging import getLogger

from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.meshnet import update_meshnet_config
from raptiformica.settings.types import get_first_server_type
from raptiformica.shell.cjdns import ensure_cjdns_installed
from raptiformica.shell.config import run_configured_bootstrap_command
from raptiformica.shell.consul import ensure_consul_installed
from raptiformica.shell.git import ensure_latest_source
from raptiformica.shell.raptiformica import mesh
from raptiformica.shell.rsync import upload_self
from raptiformica.settings.load import load_config

log = getLogger(__name__)


def retrieve_provisioning_config(server_type=get_first_server_type()):
    """
    Get the source, name and bootstrap command from the settings for the specified server type
    :param str server_type: name of the server type. i.e. headless
    :return tuple provisioning_config: tuple of source, name and bootstrap command
    """
    log.debug("Retrieving provisioning config")
    config = load_config(MUTABLE_CONFIG)
    source = config['server_types'][server_type]['source']
    name = config['server_types'][server_type]['name']
    command = config['server_types'][server_type]['bootstrap_command']
    return source, name, command


def provision_machine(host, port=22, server_type=get_first_server_type()):
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


def assimilate_machine(host, port=22):
    """
    Prepare the machine to be joined into the distributed network
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Preparing to machine to be joined into the distributed network")
    ensure_cjdns_installed(host, port=port)
    ensure_consul_installed(host, port=port)
    update_meshnet_config(host, port=port)


def deploy_meshnet(host, port=22):
    """
    Join the machine in the distributed network
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Joining the machine into the distributed network")
    # uploading self again to update the meshnet config
    upload_self(host, port=port)
    mesh(host, port=port)


def slave_machine(host, port=22, provision=True, assimilate=True, server_type=get_first_server_type()):
    """
    Provision the remote machine and optionally (default yes) assimilate it into the network.
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param bool provision: whether or not we should assimilate the remote machine
    :param bool assimilate: whether or not we should assimilate the remote machine
    :param str server_type: name of the server type to provision the machine as
    :return None:
    """
    log.info("Slaving machine {}".format(host))
    if provision:
        provision_machine(host, port=port, server_type=server_type)
    upload_self(host, port=port)
    if assimilate:
        assimilate_machine(host, port=port)
        deploy_meshnet(host, port=port)
