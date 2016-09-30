from logging import getLogger

from raptiformica.distributed.exec import try_machine_command
from raptiformica.shell.execute import run_command_print_ready, raise_failure_factory

log = getLogger(__name__)


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
