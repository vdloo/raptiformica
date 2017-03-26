from logging import getLogger

from raptiformica.distributed.ping import check_port_open
from raptiformica.settings.types import get_first_server_type
from raptiformica.shell.raptiformica import slave
from raptiformica.shell.ssh import forward_local_port, copy_id_from_remote

log = getLogger(__name__)


def verify_local_ssh_running():
    """
    Check the SSH port is open on the local machine
    :return None
    """
    log.info("Checking if SSH is running on port 22 "
             "on the local machine at 127.0.0.1")
    ssh_port_is_open = check_port_open('127.0.0.1', 22)
    if not ssh_port_is_open:
        raise RuntimeError(
            "Can not connect to port 22 on the local "
            "machine! Make sure SSH is running"
        )


def join_machine(host, port=22, server_type=None):
    """
    Provision the local machine and optionally (default yes) assimilate it
    into an existing network. The following steps will be executed to achieve
    this:

    - check if a local SSH server is running
    - reverse SSH tunnel the local SSH port to the localhost on the remote
    machine
    - copy the identity of the remote machine to the local machine
    - slave the local machine from the remote machine through the tunnel

    :param str host: hostname or ip of the remote machine to use to slave
    the local machine by reverse forwarding the local SSH port to it.
    :param int port: port to use to connect to the remote machine over ssh
    :param str server_type: name of the server type to provision the machine as
    :return None:
    """
    log.info("Joining local machine to remote host {}".format(host))
    server_type = server_type or get_first_server_type()
    verify_local_ssh_running()
    with forward_local_port(
        host, source_port=22,
        # todo: pick a random available port
        destination_port=3222,
        ssh_port=port
    ):
        log.info(
            "Allowing the remote host to perform "
            "passwordless logins on this host"
        )
        copy_id_from_remote(host, ssh_port=port)
        slave(
            # todo: forward to a prerouted IP so multiple joins can be performed.
            # Otherwise 127.0.0.1 will be removed from the shared config on the next
            # join. Also 127.0.0.1 is ambiguous for all other machines where the port
            # is not reversed forwarded to.
            host_to_slave='127.0.0.1',
            host_to_slave_port=3222,
            host=host,
            port=port,
            server_type=server_type
        )
