from os import path
from logging import getLogger

from raptiformica.settings import INSTALL_DIR
from raptiformica.utils import run_command_remotely_print_ready

log = getLogger(__name__)


def run_configured_bootstrap_command_failure(process_output):
    """
    Log the bootstrap command failure error message
    :param tuple process_output: printable process_output
    :return None:
    """
    _, standard_out, standard_error = process_output
    log.warning(
        "Failed to run configured provisioning command: {}".format(
            standard_error
        )
    )
    print(standard_out)


def run_configured_bootstrap_command_success(process_output):
    """
    Log a bootstrap command success message
    :param tuple process_output: printable process_output
    :return None:
    """
    _, standard_out, _ = process_output
    log.info("Successfully started configured provisioning command in the background")
    print(standard_out)


def run_configured_bootstrap_command(bootstrap_command, name, host, port=22):
    """
    Run the configured bootstrap command in the provisioning directory
    :param str bootstrap_command: the bootstrap command as found in the config for the server type
    :param str name: name of the bootstrap resource
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return:
    """
    log.info("Running configured bootstrap command: {}".format(bootstrap_command))

    provisioning_directory = path.join(INSTALL_DIR, name)
    configured_bootstrap_command = [
        "cd", provisioning_directory, ";", bootstrap_command
    ]
    # may deadlock if the command output buffer hits the limit.
    # should probably make this non-blocking in the future.
    return run_command_remotely_print_ready(configured_bootstrap_command, host, port=port,
                                            failure_callback=run_configured_bootstrap_command_failure,
                                            success_callback=run_configured_bootstrap_command_success)
