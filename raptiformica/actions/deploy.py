from logging import getLogger

from contextlib import suppress

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


def deploy_network(inventory, server_type=None):
    """
    Deploy or re-create the raptiformica network to the hostnames or IPs
    from the passed inventory file. Will wipe any existing raptiformica
    configuration on those machines and deploy a new network.
    :param str inventory: The inventory file
    :param str server_type: name of the server type to provision the machine as
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
    for inventory_host in inventory_hosts:
        log.info(
            "Attempting to clean up any local state on {} if "
            "any".format(inventory_host['dst'])
        )
        with suppress(RuntimeError):
            clean(inventory_host['dst'], port=inventory_host.get('port', 22))

        log.info("Slaving {}".format(inventory_host['dst']))
        slave_machine(
            inventory_host['dst'],
            port=inventory_host.get('port', 22),
            server_type=server_type
        )
