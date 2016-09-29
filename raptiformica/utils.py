import json
from itertools import chain
from os import path, makedirs, walk

from logging import getLogger
from time import sleep

log = getLogger(__name__)


def load_json(json_file):
    """
    Parse a json config file and return the data as a dict
    :param str json_file: path to the .json config file
    :return dict: the data from the config file
    """
    with open(json_file, 'r') as stream:
        return json.load(stream)


def write_json(data, json_file):
    """
    Write data to a json file
    :param mul data: data to dump to json
    :param str json_file: path to the mutable .json config file
    :return None:
    """
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)


def ensure_directory(directory):
    """
    Create a directory if it does not exist
    :param str directory: path to the directory
    :return None:
    """
    if not path.exists(directory):
        makedirs(directory)


def list_all_files_in_directory(directory):
    """
    List the absolute paths of all files in the directory recursively
    :param str directory: path to the directory to list
    :return list[str, ..] files: List of absolute file paths
    """
    return chain.from_iterable(
        map(lambda t:
            map(lambda f:
                path.join(t[0], f), t[2]),
            walk(directory)))


def list_all_files_with_extension_in_directory(directory, extension):
    """
    List the absolute paths of all files with the specified extension in the directory recursively
    :param str extension: extension that will be filtered for
    :param str directory: path to the directory to list
    :return list[str, ..] files: List of absolute file paths
    """
    file_names = list_all_files_in_directory(directory)
    return filter(lambda f: f.endswith(".{}".format(extension)), file_names)


def endswith(suffix):
    """
    Create a function that checks if the argument
    that is passed in ends with string
    :param str suffix: string to check the end for
    :return func endswith_function: a function that checks if the
    argument ends with the specified string
    """
    def string_ends_with(string):
        return str.endswith(string, suffix)
    return string_ends_with


def startswith(prefix):
    """
    Create a function that checks if the argument
    that is passed in starts with string
    :param str prefix: string to check the start for
    :return func startswith_function: a function that checks if the
    argument starts with the specified string
    """
    def string_starts_with(string):
        return str.startswith(string, prefix)
    return string_starts_with


def wait(predicate, timeout=5):
    """
    Block until the predicate returns True
    :param func predicate: function to run that should evaluate to True
    :param int timeout: how many seconds to try before erroring out?
    :return None:
    """
    waited = 0
    while True:
        if waited > timeout:
            raise TimeoutError(
                "Waited {} seconds, will not "
                "wait any longer".format(timeout)
            )
        if predicate():
            return
        else:
            waited += 1
            sleep(1)
