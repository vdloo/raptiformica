from logging import getLogger

from os import system

from raptiformica.distributed.discovery import host_and_port_pairs_from_config
from raptiformica.shell.ssh import get_ssh_connection, ssh_login_command

log = getLogger(__name__)


def ssh_connect(info_only=False):
    """
    Connect to one of the machines over SSH
    :param bool info_only: Only print connection info, don't get a shell
    :return None:
    """
    host_and_port_pairs = host_and_port_pairs_from_config()
    host, port = get_ssh_connection(host_and_port_pairs)
    if host and port:
        ssh_command = ssh_login_command(host, port=port)
        print(ssh_command) if info_only else system(ssh_command)
