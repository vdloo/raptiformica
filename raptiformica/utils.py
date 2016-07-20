import json
from subprocess import Popen, PIPE

from logging import getLogger
from raptiformica.settings import BASE_CONFIG

log = getLogger(__name__)


def load_json(json_file):
    """
    Parse a json config file and return the data as a dict
    :param str json_file: path to the .json config file
    :return dict: the data from the config file
    """
    with open(json_file, 'r') as stream:
        return json.load(stream)


def load_config(config_file=BASE_CONFIG):
    """
    Load a config file or default to the base config
    :param str config_file: path to the .json config file
    :return dict: the config data
    """
    try:
        return load_json(config_file)
    except (OSError, ValueError):
        if config_file != BASE_CONFIG:
            log.warning("Failed loading config file {}. Falling back to base config {}".format(
                config_file, BASE_CONFIG
            ))
            return load_config()
        else:
            log.error("No valid config available!")
            raise


def execute_process(command_as_list):
    """
    Execute a command locally in the shell and return the exit code, standard out and standard error as a tuple
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :return tuple (exit code, standard out, standard error):
    """
    process = Popen(command_as_list, stdout=PIPE, stderr=PIPE)
    standard_out, standard_error = process.communicate()
    exit_code = process.returncode
    return exit_code, standard_out, standard_error


def run_command(command_as_list, success_callback=lambda ret: ret, failure_callback=lambda ret: ret):
    """
    Run a command and return the exit code.
    Optionally pass a callbacks that take a tuple of (exit_code, standard out, standard error)
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :param func failure_callback: function that takes the process output tuple, runs on failure
    :param func success_callback: function that takes the process output tuple, runs on success
    """
    process_output = execute_process(command_as_list)
    exit_code, _, _ = process_output
    if exit_code != 0:
        failure_callback(process_output)
    else:
        success_callback(process_output)
    return exit_code


def run_command_print_ready(command_as_list, success_callback=lambda ret: ret, failure_callback=lambda ret: ret):
    """
    Print ready version of run_command. Un-escapes output so it can be printed.
    Optionally pass a callbacks that take a tuple of (exit_code, standard out, standard error)
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :param func failure_callback: function that takes the process output tuple, runs on failure
    :param func success_callback: function that takes the process output tuple, runs on success
    """
    return run_command(
        command_as_list,
        success_callback=print_ready_callback_factory(success_callback),
        failure_callback=print_ready_callback_factory(failure_callback)
    )


def run_command_remotely(command_as_list, host, port=22,
                         success_callback=lambda ret: ret,
                         failure_callback=lambda ret: ret):
    """
    Run a command remotely and return the exit code.
    Optionally pass a callbacks that take a tuple of (exit_code, standard out, standard error)
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param func failure_callback: function that takes the process output tuple, runs on failure
    :param func success_callback: function that takes the process output tuple, runs on success
    """
    ssh_command_as_list = ['/usr/bin/env', 'ssh',
                           'root@{}'.format(host), '-p', str(port)]
    return run_command(
        ssh_command_as_list + command_as_list,
        success_callback=success_callback, failure_callback=failure_callback
    )


def run_command_remotely_print_ready(command_as_list, host, port=22,
                                     success_callback=lambda ret: ret,
                                     failure_callback=lambda ret: ret):
    """
    Print ready version of run_command_remotely. Un-escapes output so it can be printed.
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :param func failure_callback: function that takes the process output tuple, runs on failure
    :param func success_callback: function that takes the process output tuple, runs on success
    """
    return run_command_remotely(
        command_as_list, host, port=port,
        success_callback=print_ready_callback_factory(success_callback),
        failure_callback=print_ready_callback_factory(failure_callback)
    )


def print_ready_callback_factory(callback):
    def print_ready_callback(process_output):
        callback(make_process_output_print_ready(process_output))
    return print_ready_callback


def make_process_output_print_ready(process_output):
    def un_escape_newlines(output):
        return output.decode('unicode_escape')
    exit_code, standard_out, standard_error = process_output
    return exit_code, un_escape_newlines(standard_out), un_escape_newlines(standard_error)
