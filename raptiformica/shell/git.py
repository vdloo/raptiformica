from os import path
from logging import getLogger

from raptiformica.settings import INSTALL_DIR
from raptiformica.utils import run_command_remotely, run_command_remotely_print_ready

log = getLogger(__name__)


def clone_source_failure(process_output):
    """
    Log the clone failure error message
    :param tuple process_output: printable process_output
    :return:
    """
    _, _, standard_error = process_output
    log.warning("Failed to clone source: {}".format(standard_error))


def clone_source(url, directory, host, port=22):
    """
    Clone a repository to a directory on the remote host
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str url: url to the repository to clone
    :param str directory: directory to clone it to
    :return:
    """
    log.info("Cloning {} to {}".format(url, directory))
    clone_command = ['/usr/bin/env', 'git', 'clone', url, directory]
    return run_command_remotely_print_ready(clone_command, host, port=port, failure_callback=clone_source_failure)


def pull_origin_master_failure(process_output):
    """
    Log the pull origin master failure error message
    :param tuple process_output: printable process_output
    :return None:
    """
    _, _, standard_error = process_output
    log.warning("Failed to pull origin master: {}".format(standard_error))


def pull_origin_master(directory, host, port=22):
    """
    Pull origin master in a directory on the remote machine
    :param str directory: directory on the remote machine to pull origin master in
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return int exit_code: exit code of the remote command
    """
    log.info("Pulling origin master in {}".format(directory))
    pull_origin_master_command = [
        'cd', directory, ';',
        '/usr/bin/env', 'git', 'pull', 'origin', 'master'
    ]
    return run_command_remotely_print_ready(pull_origin_master_command, host, port=port,
                                            failure_callback=pull_origin_master_failure)


def reset_hard_origin_master_failure(process_output):
    """
    Log the reset --hard origin/master failure error message
    :param tuple process_output: printable process_output
    :return None:
    """
    _, _, standard_error = process_output
    log.warning(
        "Failed to reset --hard origin/master: {}".format(standard_error)
    )


def reset_hard_origin_master(directory, host, port=22):
    """
    Reset a checkout to the trunk of the repository
    :param str directory: directory on the remote machine to reset hard origin master in
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return int exit_code: exit code of the remote command
    """
    log.info("Resetting origin master in {}".format(directory))
    reset_hard_origin_master_command = [
        'cd', directory, ';',
        '/usr/bin/env', 'git', 'reset', '--hard', 'origin/master'
    ]
    return run_command_remotely_print_ready(reset_hard_origin_master_command, host, port=port,
                                            failure_callback=reset_hard_origin_master_failure)


def update_source(directory, host, port=22):
    """
    Refresh a checked out repository
    :param str directory: directory to pull origin master and reset hard in
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Updating the repository in {}".format(directory))
    exit_code = pull_origin_master(directory, host, port=port)
    if exit_code != 0:
        reset_hard_origin_master(directory, host, port=port)


def ensure_latest_source_failure_factory(source, provisioning_directory, host, port=22):
    """
    Create a run_command callback that checks out a repository on the remote host
    :param str source: repository to clone
    :param str provisioning_directory: directory where the repo will be cloned
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return function ensure_latest_source_failure: function that takes a process_output
    """
    def ensure_latest_source_failure(_):
        log.info("Provisioning directory does not exist yet")
        clone_source(source, provisioning_directory, host, port=port)
    return ensure_latest_source_failure


def ensure_latest_source_success_factory(provisioning_directory, host, port=22):
    """
    Create a run_command callback that updates the provisioning_directory
    on the remote host
    :param str provisioning_directory: directory of the checkout to be refreshed
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return function ensure_latest_source_success: function that takes a process_output
    """
    def ensure_latest_source_success(_):
        log.info("Found an existing checkout on the remote host.")
        update_source(provisioning_directory, host, port=port)
    return ensure_latest_source_success


def ensure_latest_source(source, name, host, port=22):
    """
    Ensure a repository is checked out and the latest version in the name directory
    in the INSTALL DIR on a remote machine
    :param source: location of the the source (url)
    :param name: name of the source
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return int checkout_exists: exit code of the test -d command for the directory
    0 if the repository was freshly cloned,
    1 when there already was a checkout
    """
    log.info("Ensuring latest source for {} from {}".format(name, source))
    provisioning_directory = path.join(INSTALL_DIR, name)
    test_directory_exists_command = ['test', '-d', provisioning_directory]
    failure_callback = ensure_latest_source_failure_factory(
        source, provisioning_directory, host, port=port
    )
    success_callback = ensure_latest_source_success_factory(
        provisioning_directory, host, port=port
    )
    return run_command_remotely(test_directory_exists_command, host, port=port,
                                success_callback=success_callback, failure_callback=failure_callback)
