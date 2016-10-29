from logging import getLogger

from raptiformica.shell.execute import run_command_print_ready

log = getLogger(__name__)


def try_machine_command(host_and_port_pairs, command_as_list,
                        attempt_message="trying command on {}:{}",
                        all_failed_message="Ran out of hosts to try!",
                        attempt_limit=3):
    """
    Run the command_as_list on available remote hosts until one returns a nonzero exit code.
    At that point return the standard out output. If we ran out of host and port pairs to try,
    log a warning and return None
    :param list[tuple, ..] host_and_port_pairs: A list of tuples containing host and ports
    :param list[str, ..] command_as_list: list of strings which build up the command that will be executed
    :param str attempt_message: The message to log to debug before every attempt. Formats 'host' and 'port'
    :param str all_failed_message: The message to log as warning when we ran out of hosts to try
    :param int attempt_limit: How many hosts to try before giving up
    :return tuple(str standard_out_output, str host, str port) | tuple(None, None, None)
    """
    for host, port in host_and_port_pairs[:attempt_limit]:
        log.debug(attempt_message.format(host, port))
        exit_code, standard_out_output, _ = run_command_print_ready(
            command_as_list, host=host, port=port
        )
        if exit_code == 0:
            return standard_out_output.strip(), host, port
    log.debug(all_failed_message)
    return None, None, None
