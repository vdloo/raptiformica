from os import path
from logging import getLogger

from raptiformica.settings import INSTALL_DIR
from raptiformica.shell.execute import run_command_remotely_print_ready, log_failure_factory, log_success_factory

log = getLogger(__name__)


def run_configured_bootstrap_command(bootstrap_command, name, host, port=22):
    """
    Run the configured bootstrap command in the provisioning directory
    :param str bootstrap_command: the bootstrap command as found in the config for the server type
    :param str name: name of the bootstrap resource
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return int exit_code: exit code of the configured bootstrap command
    """
    log.info("Running configured bootstrap command: {}".format(bootstrap_command))
    provisioning_directory = path.join(INSTALL_DIR, name)
    configured_bootstrap_command = [
        "cd", provisioning_directory, ";", bootstrap_command
    ]
    exit_code, _, _ = run_command_remotely_print_ready(
        configured_bootstrap_command, host, port=port,
        failure_callback=log_failure_factory(
            "Failed to run configured provisioning command"
        ),
        success_callback=log_success_factory(
            "Successfully ran configured provisioning command"
        ),
        buffered=False
    )
    return exit_code
