from logging import getLogger

from raptiformica.settings import PROJECT_DIR, INSTALL_DIR
from raptiformica.utils import run_command_print_ready

log = getLogger(__name__)


def upload_self_success(process_output):
    """
    Log the upload self success message
    :param tuple process_output: printable process_output
    :return None:
    """
    _, standard_out, _ = process_output
    log.info("Uploaded raptiformica to the remote host:\n{}".format(standard_out))


def upload_self_failure(process_output):
    """
    Raise an error when the upload self failed and include the
    command error message output in the exc_info
    :param tuple process_output: printable process_output
    :return None:
    """
    _, _, standard_error = process_output
    raise RuntimeError("Something went wrong uploading raptiformica "
                       "to the remote host: {}".format(standard_error))


def upload_self(host, port=22):
    """
    Upload the source code of the current raptiformica checkout to the remote host.
    Excludes non-transferible var files like Virtual Machines (these should be ephemeral by nature)
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return:
    """
    log.info("Uploading raptiformica to the remote host")
    upload_command = [
        '/usr/bin/env', 'rsync', '-L', '-avz',
        PROJECT_DIR, 'root@{}:{}'.format(host, INSTALL_DIR),
        '--exclude=var/machines', '--exclude', '*.pyc',
        '-e', 'ssh -p {}'.format(port)
    ]
    return run_command_print_ready(
        upload_command,
        success_callback=upload_self_success,
        failure_callback=upload_self_failure
    )
