from logging import getLogger

from raptiformica.settings.types import get_first_server_type

log = getLogger(__name__)


def join_machine(host, port=22, provision=True, assimilate=True,
                 after_assimilate=True, after_mesh=True, server_type=None,
                 uuid=None):
    """
    Provision the local machine and optionally (default yes) assimilate it
    into an existing network.
    :param str host: hostname or ip of the remote machine to use to slave
    the local machine by reverse forwarding the local SSH port to it.
    :param int port: port to use to connect to the remote machine over ssh
    :param bool provision: whether or not we should assimilate the local machine
    :param bool assimilate: whether or not we should assimilate the local machine
    :param bool after_assimilate: whether or not we should perform the after
    assimilation hooks
    :param bool after_mesh: Whether or not to perform the after_mesh hooks
    :param str server_type: name of the server type to provision the machine as
    :param str uuid: identifier for a local compute checkout
    :return None:
    """
    log.info("Joining local machine to remote host {}".format(host))
    server_type = server_type or get_first_server_type()
