from logging import getLogger

from raptiformica.config.server import get_first_server_type
from raptiformica.settings import PROJECT_DIR, INSTALL_DIR
from raptiformica.utils import run_command

log = getLogger(__name__)


def upload_self(host, port=22):
    """
    Upload the source code of the current raptiformica checkout to the remote host.
    Excludes non-transferible var files like Virtual Machines (these should be ephemeral by nature)
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return:
    """
    upload_command = [
        '/usr/bin/env', 'rsync', '-L', '-avz',
        '{}'.format(PROJECT_DIR), 'root@{}:{}'.format(host, INSTALL_DIR),
        '--exclude=var/machines', '--exclude', '*pyc',
        '-e', 'ssh -p {}'.format(port)
    ]
    exit_code, standard_out, standard_error = run_command(upload_command)

    if exit_code != 0:
        raise RuntimeError(
            "Something went wrong uploading raptiformica to the remote host:\n{}".format(
                str(standard_error).replace('\\n', '\n')
            ))
    else:
        log.debug(str(standard_out).replace('\\n', '\n'))
        log.info("Uploaded raptiformica to the remote host")


def provision(host, port=22):
    """
    Provision the machine with the sources from the config file
    :param host:
    :param port:
    :return:
    """


def slave_machine(host, port=22, assimilate=True, server_type=get_first_server_type()):
    """
    Provision the remote machine and optionally (default yes) assimilate it into the network.
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param bool assimilate: whether or not we should assimilate the remote machine
    :param str server_type: name of the server type to provision the machine as
    :return None:
    """
    upload_self(host, port=port)
