from functools import partial
from logging import getLogger

from os.path import isfile, isdir

from raptiformica.settings import PROJECT_DIR, INSTALL_DIR, MUTABLE_CONFIG, USER_MODULES_DIR
from raptiformica.shell.execute import run_command_print_ready, raise_failure_factory, log_success_factory
from raptiformica.shell.raptiformica import create_remote_raptiformica_cache

log = getLogger(__name__)


def upload(source, destination, host, port=22):
    """
    Upload the source path from the local host to the destination path on the remote host
    :param str source: path to sync from on the local host
    :param str destination: path to sync to on the remote machine
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return bool status: success or failure
    """
    upload_command = [
        '/usr/bin/env', 'rsync', '-L', '-avz',
        source, 'root@{}:{}'.format(host, destination),
        '--exclude=.venv', '--exclude', '*.pyc',
        '-e', 'ssh -p {} '
              '-oStrictHostKeyChecking=no '
              '-oUserKnownHostsFile=/dev/null'.format(port)
    ]
    exit_code, _, _ = run_command_print_ready(
        upload_command,
        success_callback=log_success_factory(
            "Successfully uploaded files to the remote host"
        ),
        failure_callback=raise_failure_factory(
            "Something went wrong uploading files to the remote host"
        ),
        buffered=False
    )
    return exit_code


def upload_self(host, port=22):
    """
    Upload the source code of the current raptiformica checkout to the remote host.
    Excludes non-transferable var files like Virtual Machines (these should be ephemeral by nature)
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return bool status: True if success, False if failure
    """
    log.info("Uploading raptiformica to the remote host")
    upload_partial = partial(upload, host=host, port=port)
    upload_project_exit_code = upload_partial(PROJECT_DIR, INSTALL_DIR)
    create_cache_exit_code = create_remote_raptiformica_cache(host, port=port)
    upload_config_exit_code = upload_partial(
        MUTABLE_CONFIG, "$HOME/.raptiformica.d"
    ) if (isfile(MUTABLE_CONFIG) or isdir(USER_MODULES_DIR)) else 0
    return not any(
        (
            upload_project_exit_code,
            create_cache_exit_code,
            upload_config_exit_code
        )
    )
