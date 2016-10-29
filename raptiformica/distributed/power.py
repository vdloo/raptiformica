from raptiformica.distributed.exec import try_machine_command


def try_issue_shutdown(host_and_port_pairs):
    """
    Iterate over host and port pairs and try to issue a shutdown on all nodes until
    one returns a nonzero exit code. At that point return the standard out output.
    If we ran out of host and port pairs to try, log a warning and return None
    :param list[tuple, ..] host_and_port_pairs: A list of tuples containing host and ports
    of remote hosts
    :return str standard_out | None: 'consul exec' output or None
    """

    issue_global_shutdown_command = ["consul", "exec", "'shutdown -h now'"]
    attempt_message = "Trying to issue a global shutdown on {}:{}"
    all_failed_message = "Failed to issue a global shutdown on any of the nodes."
    output, _, _ = try_machine_command(
        host_and_port_pairs,
        issue_global_shutdown_command,
        attempt_message=attempt_message,
        all_failed_message=all_failed_message
    )
    return output
