from logging import getLogger

from os import system

from raptiformica.distributed.discovery import host_and_port_pairs_from_mutable_config
from raptiformica.shell.ssh import get_ssh_connection

log = getLogger(__name__)


def ssh_connect(info_only=False):
    """
    Connect to one of the machines over SSH
    :param bool info_only: Only print connection info, don't get a shell
    :return None:
    """
    host_and_port_pairs = host_and_port_pairs_from_mutable_config()
    host, port = get_ssh_connection(host_and_port_pairs)
    if host and port:
        ssh_command = "ssh root@{} -p {} " \
                      "-oStrictHostKeyChecking=no " \
                      "-oUserKnownHostsFile=/dev/null " \
                      "-oPasswordAuthentication=no".format(host, port)
        if info_only:
            print(ssh_command)
        else:
            system(ssh_command)
