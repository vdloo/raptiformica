from functools import partial
from os import path
from logging import getLogger
from shlex import quote

from raptiformica.settings import INSTALL_DIR
from raptiformica.shell.execute import run_command_print_ready, \
    log_failure_factory, run_command

log = getLogger(__name__)


def execute_clone_source_command(url, directory, run_command_function):
    """
    Pass a clone command to the run_command_function
    :param str url: url to the repository to clone
    :param str directory: directory to clone it to
    :param func run_command_function: function to pass the clone command to
    :return int exit_code: exit code of the clone source command
    """
    log.info("Cloning {} to {}".format(url, directory))
    clone_command = ['/usr/bin/env', 'git', 'clone', url, directory]
    exit_code, _, _ = run_command_function(
        clone_command,
        failure_callback=log_failure_factory("Failed to clone source"),
        buffered=False
    )
    return exit_code


def clone_source(url, directory, host=None, port=22):
    """
    Clone a repository to a directory on the specified host
    :param str host: hostname or ip of the remote machine, None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str url: url to the repository to clone
    :param str directory: directory to clone it to
    :return int exit_code: exit code of the clone source command
    """
    run_command_print_ready_partial = partial(
        run_command_print_ready, host=host, port=port
    )
    return execute_clone_source_command(
        url, directory, run_command_print_ready_partial
    )


def pull_origin_master(directory, host=None, port=22):
    """
    Pull origin master in a directory on the remote machine
    :param str directory: directory on the remote machine to pull origin master in
    :param str host: hostname or ip of the remote machine, None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return int exit_code: exit code of the remote command
    """
    log.info("Pulling origin master in {}".format(directory))
    pull_origin_master_command = 'cd {}; git pull origin master'.format(
        quote(directory)
    )
    exit_code, _, _ = run_command_print_ready(
        pull_origin_master_command, host=host, port=port,
        failure_callback=log_failure_factory(
            "Failed to pull origin master"
        ),
        buffered=False,
        shell=True
    )
    return exit_code


def reset_hard_origin_master(directory, host=None, port=22):
    """
    Reset a checkout to the trunk of the repository
    :param str directory: directory on the remote machine to reset hard origin master in
    :param str host: hostname or ip of the remote machine, or None for local
    :param int port: port to use to connect to the remote machine over ssh
    :return int exit_code: exit code of the remote command
    """
    log.info("Resetting origin master in {}".format(directory))
    reset_hard_origin_master_command = 'cd {}; git reset --hard ' \
                                       'origin/master'.format(quote(directory))
    exit_code, _, _ = run_command_print_ready(
        reset_hard_origin_master_command, host=host, port=port,
        failure_callback=log_failure_factory(
            "Failed to reset --hard origin/master"
        ),
        buffered=False,
        shell=True
    )
    return exit_code


def update_source(directory, host=None, port=22):
    """
    Refresh a checked out repository
    :param str directory: directory to pull origin master and reset hard in
    :param str host: hostname or ip of the remote machine, None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Updating the repository in {}".format(directory))
    exit_code = pull_origin_master(directory, host=host, port=port)
    if exit_code != 0:
        reset_hard_origin_master(directory, host=host, port=port)


def ensure_latest_source_failure_factory(source, provisioning_directory, host=None, port=22):
    """
    Create a run_command callback that checks out a repository on the specified host
    :param str source: repository to clone
    :param str provisioning_directory: directory where the repo will be cloned
    :param str host: hostname or ip of the remote machine, or None for the local host
    :param int port: port to use to connect to the remote machine over ssh
    :return function ensure_latest_source_failure: function that takes a process_output
    """
    def ensure_latest_source_failure(_):
        log.info("Provisioning directory does not exist yet")
        clone_source(source, provisioning_directory, host=host, port=port)
    return ensure_latest_source_failure


def ensure_latest_source_success_factory(provisioning_directory, host=None, port=22):
    """
    Create a run_command callback that updates the provisioning_directory
    on the specified host
    :param str provisioning_directory: directory of the checkout to be refreshed
    :param str host: hostname or ip of the remote machine, None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return function ensure_latest_source_success: function that takes a process_output
    """
    def ensure_latest_source_success(_):
        log.info("Found an existing checkout on the specified host.")
        update_source(provisioning_directory, host=host, port=port)
    return ensure_latest_source_success


def ensure_latest_source(source, name, host=None, port=22):
    """
    Ensure a repository is checked out and the latest version in the name directory
    in the INSTALL DIR on the specified machine
    :param source: location of the the source (url)
    :param name: name of the source
    :param str host: hostname or ip of the remote machine, None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return int checkout_exists: exit code of the test -d command for the directory
    0 if the repository was freshly cloned,
    1 when there already was a checkout
    """
    log.info("Ensuring latest source for {} from {}".format(name, source))
    provisioning_directory = path.join(INSTALL_DIR, name)
    test_directory_exists_command = ['test', '-d', provisioning_directory]

    exit_code, _, _ = run_command(
        test_directory_exists_command, host=host, port=port,
        success_callback=ensure_latest_source_success_factory(
            provisioning_directory, host=host, port=port
        ),
        failure_callback=ensure_latest_source_failure_factory(
            source, provisioning_directory, host=host, port=port
        )
    )
    return exit_code
