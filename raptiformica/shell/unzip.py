from raptiformica.shell.execute import run_critical_unbuffered_command_remotely_print_ready


def unzip(zip_file, unpack_dir, host, port=22, failure_message="Failed to unzip file"):
    """
    Unzip a file on the remote host
    :param str zip_file: path to the zip file to unzip
    :param str unpack_dir: path to the unpack directory
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str failure_message: Message to error out with if file could not
    be unzipped
    :return None:
    """
    run_critical_unbuffered_command_remotely_print_ready(
        ['unzip', '-o', zip_file, '-d', unpack_dir],
        host, port=port, failure_message=failure_message
    )
