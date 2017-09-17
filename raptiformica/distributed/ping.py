from contextlib import closing
from random import shuffle
from socket import socket, AF_INET, SOCK_STREAM
from logging import getLogger

from raptiformica.distributed.discovery import host_and_port_pairs_from_config
from raptiformica.distributed.exec import try_machine_command


log = getLogger(__name__)


def try_ping(host_and_port_pairs, host):
    """
    Iterate over host and port pairs and try to ping the host on each
    of them until one returns a nonzero exit code. At that point return the
    standard out output. If we ran out of host and port pairs to try, log a
    warning and return None
    :param list[tuple, ..] host_and_port_pairs: A list of tuples containing
    host and ports
    of remote hosts
    :param str host: The host to ping
    :return str consul_event_output | None: 'ping output' output or None
    :return tuple(str output, str success_host, int success_port) |
    tuple(None, None, None): The output of the ping and the host and port
    pair it ran on, or a tuple of Nones if none of the hosts in the host
    and port pairs could ping the provided host.
    """

    ping_remote_host = ["ping", "-c", "1", "-W", "1", host]
    attempt_message = "Trying to ping {}".format(
        host
    ) + " from {}:{}"
    all_failed_message = "Could not ping the host on any machine in the " \
                         "distributed network. Maybe no meshnet has been " \
                         "established yet."
    output, success_host, success_port = try_machine_command(
        host_and_port_pairs,
        ping_remote_host,
        attempt_message=attempt_message,
        all_failed_message=all_failed_message
    )
    return output, success_host, success_port


def find_host_that_can_ping(host):
    """
    Find a host in the cluster that can ping the specified host. Returns the
    host and port pair of the host that can ping or a tuple of None if none
    could.
    :param str host: The host to try to ping from the hosts in the network.
    :return tuple(str host, int port) | tuple(None, None): A tuple of host
    and port of the remote host in the cluster that could ping the specified
    host.
    """
    log.info("Finding a host in the network that can ping {}".format(host))
    host_and_port_pairs = host_and_port_pairs_from_config()
    shuffle(host_and_port_pairs)
    neighbour_host_and_port_pairs = [
        pair for pair in host_and_port_pairs
        if pair[0] != host
    ]
    _, access_host, access_host_ssh_port = try_ping(
        neighbour_host_and_port_pairs, host
    )
    return access_host, access_host_ssh_port


def check_port_open(host, port):
    """
    Check if a port is open on a host
    :param str host: The host to check the port on
    :param int port: The port to check
    :return bool open: True if open, False if not
    """
    log.debug("Checking if port {} is open on host {}".format(port, host))
    with closing(socket(AF_INET, SOCK_STREAM)) as s:
        return s.connect_ex((host, port)) == 0
