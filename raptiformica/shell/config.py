from os import path
from logging import getLogger

from raptiformica.settings import INSTALL_DIR
from raptiformica.shell.execute import log_failure_factory, log_success_factory, run_command_print_ready

log = getLogger(__name__)


def run_resource_command(command, name, host, port=22):
    """
    Run the command in a resource directory
    :param str command: the command to execute in the resource directory
    :param str name: name of the bootstrap resource
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return int exit_code: exit code of the configured bootstrap command
    """
    log.info("Running resource command: {}".format(command))
    provisioning_directory = path.join(INSTALL_DIR, name)
    configured_resource_command = [
        "cd", provisioning_directory, ";", command
    ]
    exit_code, _, _ = run_command_print_ready(
        configured_resource_command, host=host, port=port,
        failure_callback=log_failure_factory(
            "Failed to run resource command"
        ),
        success_callback=log_success_factory(
            "Successfully ran resource command"
        ),
        buffered=False
    )
    return exit_code
