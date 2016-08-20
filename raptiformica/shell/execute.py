from functools import partial
from subprocess import Popen, PIPE
from logging import getLogger
from sys import stdout

log = getLogger(__name__)


def raise_failure_factory(message):
    """
    Create a function that raises a failure message
    :param str message: Message to raise in combination with standard out
    :return func raise_failure:
    """
    def raise_failure(process_output):
        _, _, standard_error = process_output
        raise RuntimeError("{}\n{}".format(message, standard_error))
    return raise_failure


def log_failure_factory(message):
    """
    Create a function that logs a failure message
    :param str message: Message to log in combination with standard error
    :return func log_failure:
    """
    def log_failure(process_output):
        """
        Log a failure error message
        :param tuple process_output: printable process_output
        :return None:
        """
        _, _, standard_error = process_output
        error_message = standard_error if isinstance(
            standard_error, str
        ) else standard_error.decode()
        log.warning("{}\n{}".format(message, error_message))
    return log_failure


def log_success_factory(message):
    """
    Create a function that logs a success message
    :param str message: Message to log in combination with standard out
    :return func log_success:
    """
    def log_success(process_output):
        """
        Log a success message
        :param tuple process_output: printable process_output
        :return None:
        """
        _, standard_out, _ = process_output
        log.info("{}: {}".format(message, standard_out))
    return log_success


def execute_process(command, buffered=True, shell=False):
    """
    Execute a command locally in the shell and return the exit code, standard out and standard error as a tuple
    :param list | str command: The command as a list or as string (when shell).
    I.e. ['/bin/ls', '/root'] or "/bin/ls /root"
    :param bool buffered: Store output in a variable instead of printing it live
    :param bool shell: Run the command as in a shell and treat the command as a string instead of a list
    :return tuple (exit code, standard out, standard error):
    """
    log.debug("Running command: {}".format(command))
    process = Popen(
        command, stdout=PIPE,
        universal_newlines=buffered,
        stderr=PIPE, shell=shell,
        bufsize=-1 if buffered else 1
    )
    if not buffered:
        for line in iter(process.stdout.readline, b''):
            stdout.buffer.write(line)
            stdout.flush()
    standard_out, standard_error = process.communicate()
    exit_code = process.returncode
    return exit_code, standard_out, standard_error


def make_process_output_print_ready(process_output):
    """
    Make the process output ready to print in the terminal
    as if the process was writing to standard out directly
    :return tuple process_output: the raw process_output
    :param tuple process_output: printable process_output
    """
    def un_escape_newlines(output):
        return output if isinstance(output, str) else output.decode('unicode_escape')
    exit_code, standard_out, standard_error = process_output
    return exit_code, un_escape_newlines(standard_out), un_escape_newlines(standard_error)


def execute_process_print_ready(command, buffered=True, shell=False):
    """
    Wrapper around execute_process that first makes the returned output streams printable
    :param list | str command: The command as a list or as string (when shell).
    I.e. ['/bin/ls', '/root'] or "/bin/ls /root"
    :param bool buffered: Store output in a variable instead of printing it live
    :param bool shell: Run the command as in a shell and treat the command as a string instead of a list
    :return tuple process_output (exit code, standard out, standard error):
    """
    exit_code, standard_out, standard_error = execute_process(
        command, buffered=buffered, shell=shell
    )
    return make_process_output_print_ready(
        (exit_code, standard_out, standard_error)
    )


def run_command(command, success_callback=lambda ret: ret, failure_callback=lambda ret: ret, buffered=True, shell=False):
    """
    Run a command and return the exit code.
    Optionally pass a callbacks that take a tuple of (exit_code, standard out, standard error)
    :param list | str command: The command as a list or as string (when shell).
    I.e. ['/bin/ls', '/root'] or "/bin/ls /root"
    :param func failure_callback: function that takes the process output tuple, runs on failure
    :param func success_callback: function that takes the process output tuple, runs on success
    :param bool buffered: Store output in a variable instead of printing it live
    :param bool shell: Run the command as in a shell and treat the command as a string instead of a list
    :return tuple process_output (exit code, standard out, standard error):
    """
    process_output = execute_process(command, buffered=buffered, shell=shell)
    exit_code, standard_out, standard_error = process_output
    if exit_code != 0:
        failure_callback(process_output)
    else:
        success_callback(process_output)
    return exit_code, standard_out, standard_error


def print_ready_callback_factory(callback):
    """
    Wrap a failure or success callback in a function that first
    makes the process output printable and pass the newly
    transformed process_output into the new function
    :param func callback: success or failure callback
    :return func print_ready_callback: callback with a printable process_output
    """
    def print_ready_callback(process_output):
        callback(make_process_output_print_ready(process_output))
    return print_ready_callback


def run_command_print_ready(command, success_callback=lambda ret: ret, failure_callback=lambda ret: ret,
                            buffered=True, shell=False):
    """
    Print ready version of run_command. Un-escapes output so it can be printed.
    Optionally pass a callbacks that take a tuple of (exit_code, standard out, standard error)
    :param list | str command: The command as a list or as string (when shell).
    I.e. ['/bin/ls', '/root'] or "/bin/ls /root"
    :param func failure_callback: function that takes the process output tuple, runs on failure
    :param func success_callback: function that takes the process output tuple, runs on success
    :param bool buffered: Store output in a variable instead of printing it live
    :param bool shell: Run the command as in a shell and treat the command as a string instead of a list
    :return tuple process_output (exit code, standard out, standard error):
    """
    return run_command(
        command,
        success_callback=print_ready_callback_factory(success_callback),
        failure_callback=print_ready_callback_factory(failure_callback),
        buffered=buffered,
        shell=shell
    )


def create_in_directory_factory(directory, command_as_string, proc):
    """
    Return a partially filled out proc function which executes "command" as a string in
    the provided directory.
    :param str directory: Directory to cwd to before running the command_as_string command
    :param str command_as_string: The command as string that will be executed as sh -c 'cd directory; command'
    :param func proc: the command to use to build the partial
    :return func: partial command with the command filled in
    """
    command_as_list = [
        'sh', '-c', 'cd {}; {}'.format(directory, command_as_string)
    ]
    return partial(proc, command_as_list)


def run_command_in_directory_factory(directory, command_as_string):
    """
    Return a partially filled out run_command function which executes "command" as a string in
    the provided directory.
    :param str directory: Directory to cwd to before running the command_as_string command
    :param str command_as_string: The command as string that will be executed as sh -c 'cd directory; command'
    return func partial_run_command: run_command with the command filled in
    """
    return create_in_directory_factory(
        directory, command_as_string, run_command
    )


def run_command_print_ready_in_directory_factory(directory, command_as_string):
    """
    Return a partially filled out run_command_print_ready function which executes "command" as a string in
    the provided directory.
    :param str directory: Directory to cwd to before running the command_as_string command
    :param str command_as_string: The command as string that will be executed as sh -c 'cd directory; command'
    return func partial_run_command_print_ready: run_command_print_ready with the command filled in
    """
    return create_in_directory_factory(
        directory, command_as_string, run_command_print_ready
    )


def run_command_remotely(command_as_list, host, port=22,
                         success_callback=lambda ret: ret,
                         failure_callback=lambda ret: ret,
                         buffered=True):
    """
    Run a command remotely and return the exit code.
    Optionally pass a callbacks that take a tuple of (exit_code, standard out, standard error)
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param func failure_callback: function that takes the process output tuple, runs on failure
    :param func success_callback: function that takes the process output tuple, runs on success
    :param bool buffered: Store output in a variable instead of printing it live
    :return tuple process_output (exit code, standard out, standard error):
    """
    ssh_command_as_list = ['/usr/bin/env', 'ssh',
                           '-o', 'StrictHostKeyChecking=no',
                           '-o', 'UserKnownHostsFile=/dev/null',
                           'root@{}'.format(host), '-p', str(port)]
    return run_command(
        ssh_command_as_list + command_as_list,
        success_callback=success_callback, failure_callback=failure_callback,
        buffered=buffered
    )


def run_command_remotely_print_ready(command_as_list, host, port=22,
                                     success_callback=lambda ret: ret,
                                     failure_callback=lambda ret: ret,
                                     buffered=True):
    """
    Print ready version of run_command_remotely. Un-escapes output so it can be printed.
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param func failure_callback: function that takes the process output tuple, runs on failure
    :param func success_callback: function that takes the process output tuple, runs on success
    :param bool buffered: Store output in a variable instead of printing it live
    :return tuple process_output (exit code, standard out, standard error):
    """
    return run_command_remotely(
        command_as_list, host, port=port,
        success_callback=print_ready_callback_factory(success_callback),
        failure_callback=print_ready_callback_factory(failure_callback),
        buffered=buffered
    )


def run_critical_command_remotely_print_ready(command_as_list, host, port=22, buffered=True,
                                              failure_message='Command failed'):
    """
    A wrapper around run_command_print_ready but with a failure callback specified.
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str failure_message: message to include in the raised failure
    if the exit code is nonzero
    :param bool buffered: Store output in a variable instead of printing it live
    :return tuple process_output (exit code, standard out, standard error):
    """
    return run_command_remotely_print_ready(
        command_as_list,
        host, port=port,
        failure_callback=raise_failure_factory(
            failure_message
        ),
        buffered=buffered
    )


def run_critical_unbuffered_command_remotely_print_ready(command_as_list, host, port=22,
                                                         failure_message='Command failed'):
    """
    Wrapper around run_critical_command_remotely_print_ready but with output to
    standard out instead of capturing it.
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str failure_message: message to include in the raised failure
    if the exit code is nonzero
    :return tuple process_output (exit code, standard out, standard error):
    """
    return run_critical_command_remotely_print_ready(
        command_as_list, host, port=port,
        failure_message=failure_message,
        buffered=False
    )


def run_remote_multiple_labeled_commands(distro_command_iterable, host, port=22,
                                         failure_message='Command failed for label {}'):
    """
    Takes a iterable of iterables with label and command_as_string and runs the
    command remotely and unbuffered, raising an error if it fails.


    :param iterable[iterable] distro_command_iterable: iterable of pairs containing
    label and a command as string
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str failure_message: message to include in the raised failure
    if the exit code is nonzero. Should contain a {} to format the label.
    :return None
    """
    for label, command_as_string in distro_command_iterable:
        run_critical_unbuffered_command_remotely_print_ready(
            ["sh", "-c", command_as_string], host, port=port,
            failure_message=failure_message.format(label)
        )
