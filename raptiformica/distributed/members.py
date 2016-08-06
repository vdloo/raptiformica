from raptiformica.distributed.exec import try_machine_command


def try_get_members_list(host_and_port_pairs):
    """
    Iterate over host and port pairs and try to list the members list on each
    of them until one returns a nonzero exit code. At that point return the standard
    out output. If we ran out of host and port pairs to try, log a warning and return None
    :param list[tuple, ..] host_and_port_pairs: A list of tuples containing host and ports
    of remote hosts
    :return str members_list | None: 'consul_members' output or None
    """

    list_members_command = ["consul", "members"]
    attempt_message = "Trying to get members list from {}:{}"
    all_failed_message = "Could not list members in the distributed network. " \
                         "Maybe no meshnet has been established yet. " \
                         "Do you have at least three machines running?"
    return try_machine_command(
        host_and_port_pairs,
        list_members_command,
        attempt_message=attempt_message,
        all_failed_message=all_failed_message
    )
