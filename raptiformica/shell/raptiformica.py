from logging import getLogger

from raptiformica.settings import RAPTIFORMICA_DIR
from raptiformica.shell.execute import run_command_print_ready_in_directory_factory, raise_failure_factory, \
    run_command_remotely_print_ready

log = getLogger(__name__)


def run_raptiformica_command(command_as_string, host, port=22):
    """
    Run a command in the raptiformica directory on a remote machine.
    :param str command_as_string: Command to run. i.e ./bin/raptiformica_mesh.py
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return int exit_code: Exit code from the ./bin/raptiformica_mesh.py command
    """
    log.info("Running raptiformica command on "
             "remote host: {}".format(command_as_string))
    exit_code, _, _ = run_command_remotely_print_ready(
        ['sh', '-c', '"cd {}; {}"'.format(
            RAPTIFORMICA_DIR, command_as_string
        )],
        host, port=port,
        failure_callback=raise_failure_factory(
            "Failed to run raptiformica command on remote host"
        ),
        buffered=False,
    )
    return exit_code


def mesh(host, port=22):
    """
    Run ./bin/raptiformica_mesh.py on a remote machine.
    This command uses the mutable config to configure the
    meshnet services and joins the network or bootstraps a
    new one if there are enough machines.
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return int exit_code: Exit code from the ./bin/raptiformica_mesh.py command
    """
    log.info("Joining the remote host into the distributed network")
    # todo: let the remote raptiformica command use the same logging level
    # as the current process
    return run_raptiformica_command(
        "export PYTHONPATH=.; ./bin/raptiformica_mesh.py --verbose",
        host, port=port
    )
