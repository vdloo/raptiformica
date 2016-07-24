from functools import partial
from subprocess import Popen, PIPE

from logging import getLogger

log = getLogger(__name__)


def raise_failure_factory(message):
    """
    Create a function that raises a failure message
    :param str message: Message to raise in combination with standard out
    :return func raise_failure:
    """
    def raise_failure(process_output):
        _, _, standard_error = process_output
        raise RuntimeError("{}: {}".format(message, standard_error))
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
        log.warning("{}: {}".format(message, standard_error))
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


def execute_process(command_as_list, buffered=True):
    """
    Execute a command locally in the shell and return the exit code, standard out and standard error as a tuple
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :param bool buffered: Store output in a variable instead of printing it live
    :return tuple (exit code, standard out, standard error):
    """
    log.debug("Running command: {}".format(command_as_list))
    process = Popen(
        command_as_list, stdout=PIPE,
        stderr=PIPE, universal_newlines=True
    )
    if not buffered:
        for line in process.stdout:
            print(line, end='')
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


def execute_process_print_ready(command_as_list, buffered=True):
    """
    Wrapper around execute_process that first makes the returned output streams printable
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :param bool buffered: Store output in a variable instead of printing it live
    :return tuple process_output (exit code, standard out, standard error):
    """
    exit_code, standard_out, standard_error = execute_process(
        command_as_list, buffered=buffered
    )
    return make_process_output_print_ready(
        (exit_code, standard_out, standard_error)
    )


def run_command(command_as_list, success_callback=lambda ret: ret, failure_callback=lambda ret: ret, buffered=True):
    """
    Run a command and return the exit code.
    Optionally pass a callbacks that take a tuple of (exit_code, standard out, standard error)
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :param func failure_callback: function that takes the process output tuple, runs on failure
    :param func success_callback: function that takes the process output tuple, runs on success
    :param bool buffered: Store output in a variable instead of printing it live
    :return tuple process_output (exit code, standard out, standard error):
    """
    process_output = execute_process(command_as_list, buffered=buffered)
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


def run_command_print_ready(command_as_list, success_callback=lambda ret: ret, failure_callback=lambda ret: ret,
                            buffered=True):
    """
    Print ready version of run_command. Un-escapes output so it can be printed.
    Optionally pass a callbacks that take a tuple of (exit_code, standard out, standard error)
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :param func failure_callback: function that takes the process output tuple, runs on failure
    :param func success_callback: function that takes the process output tuple, runs on success
    :param bool buffered: Store output in a variable instead of printing it live
    :return tuple process_output (exit code, standard out, standard error):
    """
    return run_command(
        command_as_list,
        success_callback=print_ready_callback_factory(success_callback),
        failure_callback=print_ready_callback_factory(failure_callback),
        buffered=buffered
    )


def run_command_print_ready_in_directory_factory(directory, command_as_string):
    """
    Return a partially filled out run_command_print_ready function which executes "command" as a string in
    the provided directory.
    :param str directory: Directory to cwd to before running the command_as_string command
    :param str command_as_string: The command as string that will be executed as sh -c 'cd directory; command'
    return func partial_run_command_print_ready: run_command_print_ready with the command filled in
    """
    command_as_list = [
        'sh', '-c', 'cd {}; {}'.format(directory, command_as_string)
    ]
    return partial(run_command_print_ready, command_as_list)


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
                           'root@{}'.format(host), '-p', str(port),
                           '-o', 'StrictHostKeyChecking=no']
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
