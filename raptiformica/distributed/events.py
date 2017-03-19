from logging import getLogger

from raptiformica.distributed.discovery import host_and_port_pairs_from_config
from raptiformica.distributed.exec import try_machine_command


log = getLogger(__name__)


def try_send_consul_event(host_and_port_pairs, event_name):
    """
    Iterate over host and port pairs and try to send the event on each
    of them until one returns a nonzero exit code. At that point return the standard
    out output. If we ran out of host and port pairs to try, log a warning and return None
    :param list[tuple, ..] host_and_port_pairs: A list of tuples containing host and ports
    of remote hosts
    :param str event_name: Name of the event to send
    :return str consul_event_output | None: 'consul event' output or None
    """

    notify_cluster_change = ["consul", "event", "-name={}".format(event_name)]
    attempt_message = "Trying to send {} event".format(
        event_name
    ) + " on {}:{}"
    all_failed_message = "Could not send the event on any machine in the " \
                         "distributed network. Maybe no meshnet has been " \
                         "established yet."
    output, _, _ = try_machine_command(
        host_and_port_pairs,
        notify_cluster_change,
        attempt_message=attempt_message,
        all_failed_message=all_failed_message
    )
    return output


def send_reload_meshnet():
    """
    Refresh the cjdroute config and the consul config,
    then reload the agents if necessary. When a new machine
    is added to the network from the commandline of a machine
    that is not in the network then that new machine will be
    registered as a neighbour in the key value store of the
    other bound machines on the machine running the commands.
    However, updating the neighbours in the kv store is not
    enough if the new machine can not directly reach the other
    bound machines but the bound machines can reach the new machine.
    In that case the bound machines (or at least one) will have to
    add the new machine to their cjdroute config so they will reach
    out to it and as soon as it comes online it will be able to contact
    the bound nodes through the reverse tunnel transparently. By reloading
    the meshnet configs this is achieved.
    Note: If no consensus has been established yet this approach won't
    work since the neighbour details will not be available to the peers.
    In that case the system will try to establish a connection to the peer
    synchronously.
    :return None:
    """
    log.info(
        "Sending a meshnet config reload to all available machines"
    )
    # The 'notify_cluster_change' triggers the 'cluster_change_handler'
    # watcher handler in the consul agent config. See actions/mesh.py
    host_and_port_pairs = host_and_port_pairs_from_config()
    try_send_consul_event(host_and_port_pairs, "notify_cluster_change")
