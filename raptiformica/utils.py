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


def run_command(command_as_list):
    """
    Run a command locally in the shell and return the exit code, standard out and standard error as a tuple
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :return tuple (exit code, standard out, standard error):
    """
    process = Popen(command_as_list, stdout=PIPE, stderr=PIPE)
    standard_out, standard_error = process.communicate()
    exit_code = process.returncode
    return exit_code, standard_out, standard_error
