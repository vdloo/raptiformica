from logging import getLogger

from raptiformica.settings import PROJECT_DIR, INSTALL_DIR
from raptiformica.shell.execute import run_command_print_ready, raise_failure_factory, log_success_factory

log = getLogger(__name__)


def upload_self(host, port=22):
    """
    Upload the source code of the current raptiformica checkout to the remote host.
    Excludes non-transferable var files like Virtual Machines (these should be ephemeral by nature)
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return:
    """
    log.info("Uploading raptiformica to the remote host")
    upload_command = [
        '/usr/bin/env', 'rsync', '-L', '-avz',
        PROJECT_DIR, 'root@{}:{}'.format(host, INSTALL_DIR),
        '--exclude=var/machines', '--exclude', '*.pyc',
        '-e', 'ssh -p {} -oStrictHostKeyChecking=no'.format(port)
    ]
    exit_code, _, _ = run_command_print_ready(
        upload_command,
        success_callback=log_success_factory(
            "Uploaded raptiformica to the remote host"
        ),
        failure_callback=raise_failure_factory(
            "Something went wrong uploading raptiformica to the remote host"
        ),
        buffered=False
    )
    return exit_code
