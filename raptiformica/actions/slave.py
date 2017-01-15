from logging import getLogger

from raptiformica.settings import conf
from raptiformica.settings.load import get_config
from raptiformica.settings.meshnet import ensure_route_to_new_neighbour
from raptiformica.settings.types import get_first_server_type
from raptiformica.shell.config import run_resource_command
from raptiformica.shell.git import ensure_latest_source_from_artifacts
from raptiformica.shell.hooks import fire_hooks
from raptiformica.shell.raptiformica import mesh
from raptiformica.shell.rsync import upload_self, download_artifacts

log = getLogger(__name__)


def retrieve_provisioning_configs(server_type=None):
    """
    Get the source, name and bootstrap commands from the settings for the specified server type
    :param str server_type: name of the server type. i.e. headless
    :return list provisioning_configs: dict of provisioning configs
    """
    log.debug("Retrieving provisioning config")
    server_type = server_type or get_first_server_type()
    config = get_config()
    server_types = config[conf().KEY_VALUE_PATH]['server']
    server_type = server_types.get(server_type, {})
    return {k: {'source': v['source'], 'bootstrap': v['bootstrap']}
            for k, v in server_type.items()}


def provision_machine(host=None, port=22, server_type=None):
    """
    Deploy the bootstrapping repo on the remote machine and run the bootstrap command
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str server_type: name of the server type. i.e. headless
    :return None:
    """
    server_type = server_type or get_first_server_type()
    log.info("Provisioning host {} as server type {}".format(
        host or 'local machine', server_type
    ))
    server_type = server_type or get_first_server_type()
    provisioning_configs = retrieve_provisioning_configs(server_type)
    for name, config in provisioning_configs.items():
        log.info("Provisioning for {}".format(name))
        ensure_latest_source_from_artifacts(
            config['source'], name, host=host, port=port
        )
        run_resource_command(config['bootstrap'], name, host=host, port=port)


def assimilate_machine(host, port=22, uuid=None):
    """
    Prepare the machine to be joined into the distributed network
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str uuid: identifier for a local compute checkout
    :return None:
    """
    log.info("Preparing to machine to be joined into the distributed network")
    download_artifacts(host, port=port)
    ensure_route_to_new_neighbour(host, port=port, compute_checkout_uuid=uuid)


def deploy_meshnet(host, port=22, after_mesh=True):
    """
    Join the machine in the distributed network
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param bool after_mesh: Whether or not to perform the after_mesh hooks
    :return None:
    """
    log.info("Joining the machine into the distributed network")
    # uploading self again to update the meshnet config
    upload_self(host, port=port)
    mesh(host, port=port, after_mesh=after_mesh)


def slave_machine(host, port=22, provision=True, assimilate=True,
                  after_assimilate=True, after_mesh=True, server_type=None,
                  uuid=None):
    """
    Provision the remote machine and optionally (default yes) assimilate it
    into the network.
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param bool provision: whether or not we should assimilate the remote machine
    :param bool assimilate: whether or not we should assimilate the remote machine
    :param bool after_assimilate: whether or not we should perform the after
    assimilation hooks
    :param bool after_mesh: Whether or not to perform the after_mesh hooks
    :param str server_type: name of the server type to provision the machine as
    :param str uuid: identifier for a local compute checkout
    :return None:
    """
    log.info("Slaving machine {}".format(host))
    server_type = server_type or get_first_server_type()
    upload_self(host, port=port)
    if provision:
        provision_machine(host, port=port, server_type=server_type)
    fire_hooks('after_slave')
    if assimilate:
        assimilate_machine(host, port=port, uuid=uuid)
        deploy_meshnet(host, port=port, after_mesh=after_mesh)
        if after_assimilate:
            fire_hooks('after_assimilate')
