from functools import partial
from logging import getLogger

from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.meshnet import update_meshnet_config
from raptiformica.settings.types import get_first_server_type
from raptiformica.shell.cjdns import ensure_cjdns_installed
from raptiformica.shell.config import run_resource_command
from raptiformica.shell.consul import ensure_consul_installed
from raptiformica.shell.git import ensure_latest_source
from raptiformica.shell.hooks import fire_hooks
from raptiformica.shell.raptiformica import mesh
from raptiformica.shell.rsync import upload_self
from raptiformica.settings.load import load_config, get_config_value

log = getLogger(__name__)


def retrieve_provisioning_config(server_type=None):
    """
    Get the source, name and bootstrap command from the settings for the specified server type
    :param str server_type: name of the server type. i.e. headless
    :return tuple provisioning_config: tuple of source, name and bootstrap command
    """
    log.debug("Retrieving provisioning config")
    server_type = server_type or get_first_server_type()
    config = load_config(MUTABLE_CONFIG)
    return tuple(
        map(
            partial(
                get_config_value,
                config['server_types'][server_type]
            ),
            (
                "source",
                "name",
                "bootstrap_command"
            )
        )
    )


def provision_machine(host, port=22, server_type=None):
    """
    Deploy the bootstrapping repo on the remote machine and run the bootstrap command
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str server_type: name of the server type. i.e. headless
    :return None:
    """
    server_type = server_type or get_first_server_type()
    log.info("Provisioning host {} as server type {}".format(host, server_type))
    server_type = server_type or get_first_server_type()
    source, name, command = retrieve_provisioning_config(server_type)
    ensure_latest_source(source, name, host, port=port)
    run_resource_command(command, name, host, port=port)


def assimilate_machine(host, port=22, uuid=None):
    """
    Prepare the machine to be joined into the distributed network
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str uuid: identifier for a local compute checkout
    :return None:
    """
    log.info("Preparing to machine to be joined into the distributed network")
    ensure_cjdns_installed(host, port=port)
    ensure_consul_installed(host, port=port)
    update_meshnet_config(host, port=port, uuid=uuid)


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


def slave_machine(host, port=22, provision=True, assimilate=True, server_type=None, uuid=None):
    """
    Provision the remote machine and optionally (default yes) assimilate it into the network.
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param bool provision: whether or not we should assimilate the remote machine
    :param bool assimilate: whether or not we should assimilate the remote machine
    :param str server_type: name of the server type to provision the machine as
    :param str uuid: identifier for a local compute checkout
    :return None:
    """
    log.info("Slaving machine {}".format(host))
    server_type = server_type or get_first_server_type()
    if provision:
        provision_machine(host, port=port, server_type=server_type)
    upload_self(host, port=port)
    fire_hooks('after_slave')
    if assimilate:
        assimilate_machine(host, port=port, uuid=uuid)
        deploy_meshnet(host, port=port)
        fire_hooks('after_assimilate')
