from logging import getLogger
from shlex import quote

from raptiformica.settings import conf, Config
from raptiformica.settings.types import get_first_server_type
from raptiformica.shell.execute import raise_failure_factory, run_command_remotely, run_command_print_ready

log = getLogger(__name__)


def create_remote_raptiformica_cache(host, port=22):
    """
    Create the cache dir on a remote host
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return int exit_code: Exit code from the remote mkdir command
    """
    log.info("Ensuring remote raptiformica cache directory")
    exit_code, _, _ = run_command_remotely(
        ["mkdir", "-p", "$HOME/{}".format(Config.CACHE_DIR)],
        host, port=port, buffered=False
    )
    return exit_code


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
    exit_code, _, _ = run_command_print_ready(
        ['sh', '-c', '"cd {}; {}"'.format(
            conf().RAPTIFORMICA_DIR, command_as_string
        )],
        host=host, port=port,
        failure_callback=raise_failure_factory(
            "Failed to run raptiformica command on remote host"
        ),
        buffered=False,
    )
    log.info("Finished running the remote command on {}!".format(host))
    return exit_code


def mesh(host, port=22, after_mesh=True):
    """
    Run ./bin/raptiformica_mesh.py on a remote machine.
    This command uses the mutable config to configure the
    meshnet services and joins the network or bootstraps a
    new one if there are enough machines.
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param bool after_mesh: Whether or not to perform the after_mesh hooks
    :return int exit_code: Exit code from the ./bin/raptiformica_mesh.py command
    """
    log.info("Joining the remote host into the distributed network")
    # todo: let the remote raptiformica command use the same logging level
    # as the current process
    return run_raptiformica_command(
        "export PYTHONPATH=.; ./bin/raptiformica_mesh.py"
        "{}".format('' if after_mesh else ' --no-after-mesh'),
        host, port=port
    )


def inject(host_to_inject, host_to_inject_port, host, port=22):
    """
    Inject a host into the meshnet config on a remote machine
    :param str host_to_inject: hostname of the host to inject
    :param int host_to_inject_port: ssh port of the host to inject
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return int exit_code: Exit code from the ./bin/raptiformica_inject.py command
    """
    log.info("Injecting the specified host on the remote host")
    return run_raptiformica_command(
        "export PYTHONPATH=.; ./bin/raptiformica_inject.py "
        "--verbose {} --port {}".format(
            quote(host_to_inject),
            quote(str(host_to_inject_port))
        ),
        host, port=port
    )


def slave(host_to_slave, host_to_slave_port, host, port=22, server_type=None):
    """
    Slave a host into the meshnet config on a remote machine
    :param str host_to_slave: hostname of the host to slave
    :param int host_to_slave_port: ssh port of the host to slave
    from the remote machine
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str server_type: name of the server type to provision the machine as
    :return int exit_code: Exit code from the ./bin/raptiformica_slave.py command
    """
    server_type = server_type or get_first_server_type()
    log.info("Slaving the specified host from the remote host")
    return run_raptiformica_command(
        "export PYTHONPATH=.; ./bin/raptiformica_slave.py "
        "--verbose {} --port {} --server-type {}".format(
            quote(host_to_slave),
            quote(str(host_to_slave_port)),
            server_type
        ),
        host, port=port
    )
