from functools import partial
from logging import getLogger

from contextlib import suppress
from multiprocessing.pool import ThreadPool

from raptiformica.actions.slave import slave_machine
from raptiformica.shell.raptiformica import clean
from raptiformica.utils import load_json

log = getLogger(__name__)


def read_inventory_file(inventory):
    """
    Read an inventory file, return the list of dicts
    :param str inventory: The inventory file
    :return list[dict, ..]: List of hostname and IP definitions
    """
    log.info("Reading and validating inventory file")
    inventory_hosts = load_json(inventory)
    if not all('dst' in i for i in inventory_hosts):
        raise ValueError(
            "Not all inventory items specified a "
            "destination like {'dst': '1.2.3.4'}"
        )
    all_dst = [i['dst'] for i in inventory_hosts]
    all_via = filter(None, [i.get('via') for i in inventory_hosts])
    if not set(all_via).issubset(all_dst):
        raise ValueError(
            "Specified a 'via' item that "
            "is not defined as a 'dst' item."
        )
    # Note that there is no cycle detection here
    if any(i['dst'] == i.get('via') for i in inventory_hosts):
        raise ValueError(
            "You can not specify the "
            "same 'via' as 'dst' for one item"
        )
    return inventory_hosts


# TODO: add unit tests for this function in the file
# tests/unit/raptiformica/actions/deploy/test_deploy_to_host.py
def _deploy_to_host(
        host, server_type, provision=False,
        assimilate=False, after_assimilate=False,
        after_mesh=False
):
    """
    Remove any previously existing raptiformica
    state from a remote host and (re)deploy to it.

    :param dict host: The host to deploy to
    :param str server_type: The server type
    :param bool provision: whether or not we should assimilate the remote machine
    :param bool assimilate: whether or not we should assimilate the remote machine
    :param bool after_assimilate: whether or not we should perform the after
    assimilation hooks
    :param bool after_mesh: Whether or not to perform the after_mesh hooks
    :return None:
    """
    log.info(
        "Attempting to clean up any local state on {} if "
        "any".format(host['dst'])
    )
    # Broad exception clauses because host might be down.
    # If so, we'll get it next time.
    with suppress(Exception):
        clean(host['dst'], port=host.get('port', 22))

    log.info("Slaving {}".format(host['dst']))
    with suppress(Exception):
        slave_machine(
            host['dst'],
            port=host.get('port', 22),
            server_type=server_type,
            provision=provision,
            assimilate=assimilate,
            after_assimilate=after_assimilate,
            after_mesh=after_mesh
        )


def deploy_network(inventory, server_type=None, concurrent=5,
                   provision=False, assimilate=False,
                   after_assimilate=False, after_mesh=False):
    """
    Deploy or re-create the raptiformica network to the hostnames or IPs
    from the passed inventory file. Will wipe any existing raptiformica
    configuration on those machines and deploy a new network.
    :param str inventory: The inventory file
    :param str server_type: name of the server type to provision the machine as
    :param int concurrent: The amount of hosts to deploy to concurrently
    :param bool provision: whether or not we should assimilate the remote machine
    :param bool assimilate: whether or not we should assimilate the remote machine
    :param bool after_assimilate: whether or not we should perform the after
    assimilation hooks
    :param bool after_mesh: Whether or not to perform the after_mesh hooks
    :return None:
    """
    inventory_hosts = read_inventory_file(inventory)

    if any(i.get('via') for i in inventory_hosts):
        raise RuntimeError(
            "Via hosts are not supported yet. Please set up "
            "ProxyCommand tunnels in your .ssh/config "
            "instead for now."
        )

    log.info(
        "Will deploy a new network on {} "
        "hosts".format(len(inventory_hosts))
    )
    pool = ThreadPool(processes=concurrent)
    deploy_to_host = partial(
        _deploy_to_host,
        provision=provision,
        assimilate=assimilate,
        after_assimilate=after_assimilate,
        after_mesh=after_mesh
    )
    pool.starmap(
        deploy_to_host,
        zip(
            inventory_hosts,
            [server_type] * len(inventory_hosts)
        )
    )
