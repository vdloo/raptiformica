from contextlib import contextmanager
from logging import getLogger
from time import sleep

from uuid import uuid4

from raptiformica.distributed.exec import try_machine_command
from raptiformica.shell.execute import run_command_print_ready, raise_failure_factory, run_critical_command_print_ready

log = getLogger(__name__)


def ssh_login_command(host, port=22):
    """
    Return the SSH shell command that can be used to log in to remote machine
    :param str host: Host to log in to
    :param int port: Port to connect with
    :return str ssh_command: An SSH command
    """
    ssh_command = "ssh root@{} -p {} " \
                  "-oStrictHostKeyChecking=no " \
                  "-oUserKnownHostsFile=/dev/null " \
                  "-oPasswordAuthentication=no".format(host, port)
    return ssh_command


def verify_ssh_agent_running():
    """
    Make sure the local machine has an SSH agent running
    :return int exit_code: the exit code of the SSH agent verification command
    """
    log.info("Verifying SSH agent is running on the local machine")
    verify_agent_command = ['ssh-add', '-l']
    exit_code, standard_out, _ = run_command_print_ready(
        verify_agent_command,
        failure_callback=raise_failure_factory(
            "There is no SSH agent running on the host or there are no keys in this agent.\n"
            "Please load your ssh agent by running: "
            "eval $(ssh-agent -s); ssh-add"
        )
    )
    return exit_code


def get_ssh_connection(host_and_port_pairs):
    """
    Iterate over host and port pairs and try to connect over ssh on each
    machine until one returns a nonzero exit code trying to run a command.
    At that point return the host_and_port pair
    :param list[tuple, ..] host_and_port_pairs: A list of tuples containing host and ports
    :return tuple host_and_port_pair: host and port pair
    """
    log.debug(
        "Finding the first available machine we can log in to"
    )
    check_connection_command = ["/bin/echo", "1"]
    attempt_message = "Trying to get a shell on {}:{}"
    all_failed_message = "Failed to get an SSH connection. No available."
    _, host, port = try_machine_command(
        host_and_port_pairs,
        check_connection_command,
        attempt_message=attempt_message,
        all_failed_message=all_failed_message
    )
    return host, port


def run_detached_command(command, failure_message='Failed running detached command'):
    """
    Run a detached command and return the PID
    :param str command: The command as string
    :param str failure_message: Message of the error to raise if the command fails
    :return str uuid: name of the detached screen running the command
    """
    screen_name = str(uuid4()).replace('-', '')
    detached_command = "/usr/bin/env screen -S {} -d -m bash -c '{}'".format(
        screen_name, command
    )
    exit_code, standard_out, _ = run_critical_command_print_ready(
        detached_command, buffered=False, shell=True,
        failure_message=failure_message
    )
    return screen_name


@contextmanager
def detached_command_context(command):
    """
    Run code in a detached command context. The command is executed,
    detached and cleaned up after the context exists.
    :param str command: Command to run in the background
    :return None:
    """
    log.debug("Starting detached command {}".format(command))
    screen_name = run_detached_command(command)
    try:
        yield
    finally:
        log.debug("Killing detached command running in screen {}".format(
            screen_name
        ))
        run_command_print_ready(
            "pkill -9 -f {}".format(screen_name), shell=True
        )


@contextmanager
def forward_remote_port(host, source_port, destination_port=None, ssh_port=22, timeout=600):
    """
    Forward the remote port of any of the machines in the cluster
    :param str host: Host to forward the port from
    :param int source_port: Remote port to forward
    :param int destination_port: Destination port on the localhost to forward to.
    Defaults to source_port
    :param int ssh_port: SSH port of the remote host
    :param int timeout: Clean up tunnel after a certain time
    :return None:
    """
    ssh_command = ssh_login_command(host, port=ssh_port)
    destination_port = destination_port or source_port
    tunnel_command = '{} -L {}:localhost:{} sleep {}'.format(
        ssh_command, source_port, destination_port, timeout
    )
    log.debug("Forwarding port {} from host {} to local port {}".format(
        destination_port, host, source_port
    ))
    with detached_command_context(tunnel_command):
        # Give the tunnel some time to be established
        # todo: replace this with a block until ping
        sleep(1)
        yield
