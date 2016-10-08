from logging import getLogger

from raptiformica.settings import KEY_VALUE_PATH
from raptiformica.settings.load import get_config
from raptiformica.settings.meshnet import update_meshnet_config
from raptiformica.settings.types import get_first_server_type
from raptiformica.shell.config import run_resource_command
from raptiformica.shell.git import ensure_latest_source
from raptiformica.shell.hooks import fire_hooks
from raptiformica.shell.raptiformica import mesh
from raptiformica.shell.rsync import upload_self, download_artifacts
from raptiformica.utils import endswith, startswith

log = getLogger(__name__)


def retrieve_provisioning_configs(server_type=None):
    """
    Get the source, name and bootstrap commands from the settings for the specified server type
    :param str server_type: name of the server type. i.e. headless
    :return list provisioning_configs: dict of provisioning configs
    """
    log.debug("Retrieving provisioning config")
    server_type = server_type or get_first_server_type()
    mapped = get_config()

    server_path = '{}/server/{}'.format(
        KEY_VALUE_PATH, server_type,
    )
    server_path_keys = list(filter(
        startswith(server_path),
        mapped
    ))

    names = set(map(
        lambda x: x.split('/')[3],
        server_path_keys
    ))

    def get_item_for_name(name, item):
        return mapped[next(
            filter(
                endswith("{}/{}/{}".format(
                    server_path, name, item
                )),
                mapped
            )
        )]

    return {
        name: {
            item: get_item_for_name(name, item) for item in (
                'source', 'bootstrap'
            )
        } for name in names
    }


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
    provisioning_configs = retrieve_provisioning_configs(server_type)
    for name, config in provisioning_configs.items():
        log.info("Provisioning for {}".format(name))
        ensure_latest_source(config['source'], name, host, port=port)
        run_resource_command(config['bootstrap'], name, host, port=port)


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
    update_meshnet_config(host, port=port, compute_checkout_uuid=uuid)


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
    upload_self(host, port=port)
    if provision:
        provision_machine(host, port=port, server_type=server_type)
    fire_hooks('after_slave')
    if assimilate:
        assimilate_machine(host, port=port, uuid=uuid)
        deploy_meshnet(host, port=port)
        fire_hooks('after_assimilate')
