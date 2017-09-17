from os import path
from logging import getLogger
from shlex import quote

from raptiformica.settings import conf
from raptiformica.shell.execute import log_success_factory, run_command_print_ready, \
    raise_failure_factory
from raptiformica.utils import retry

log = getLogger(__name__)

RESOURCE_COMMAND_TIMEOUT = 60


@retry(attempts=3, expect=(RuntimeError, TimeoutError))
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
    provisioning_directory = path.join(conf().INSTALL_DIR, name)
    configured_resource_command = "cd {}; {}".format(
        quote(provisioning_directory), command
    )
    exit_code, _, _ = run_command_print_ready(
        configured_resource_command, host=host, port=port,
        failure_callback=raise_failure_factory(
            "Resource command exited nonzero, that might not be a problem. "
            "If something serious went wrong we'll try again next run."
        ),
        success_callback=log_success_factory(
            "Successfully ran resource command"
        ),
        buffered=False,
        shell=True,
        timeout=RESOURCE_COMMAND_TIMEOUT
    )
    return exit_code
