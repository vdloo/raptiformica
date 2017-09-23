import hashlib
import json
from contextlib import suppress
from time import time
from copy import deepcopy
from functools import wraps
from itertools import chain
from os import path, makedirs, walk

from logging import getLogger
from time import sleep

from os.path import getmtime

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
    with suppress(FileExistsError):
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


def retry(attempts=2, expect=(RuntimeError,)):
    """
    Decorator that retries the wrapped body until the attempts
    run out when the expected exception is encountered.
    :param int attempts: Amount of tries to perform
    :param iterable expect: Iterable of exceptions to expect
    :return func decorator: The decorator
    """
    def retry_decorator(func):
        """
        The decorator that wraps the function
        :param func func: The function to decorate
        :return func: The wrapped function
        """
        def retry_wrapper(*args, **kwargs):
            """
            The retry wrapper
            :param args: The args
            :param kwargs: The kwargs
            :return mul result: The wrapped function result
            """
            attempts_left = deepcopy(attempts)
            while True:
                attempts_left -= 1
                try:
                    return func(*args, **kwargs)
                except expect:
                    if attempts_left <= 0:
                        log.warning(
                            "Ran out of attempts for this function! Not "
                            "catching expected exception anymore."
                        )
                        raise
                    else:
                        log.info(
                            "Caught expected exception, have {} attempts "
                            "left".format(attempts_left)
                        )
        return wraps(func)(retry_wrapper)
    return retry_decorator


def group_n_elements(elements, n=1):
    """
    Return a list of sublists containing n elements of parameter iterator elements
    :param iterator elements: Iterator of elements to make groups of
    :param int n: How many items per group
    :return list groups: The grouped sublists in a list
    """
    groups = list(map(list, zip(*[iter(elements)] * n)))
    left = len(elements) % n if n else False
    if left:
        groups.append(elements[-left:])
    return groups


def calculate_checksum(filename):
    """
    Calculate the sha1 checksum of a file (in chunks)
    :param str filename: The file to calculate the checksum of
    :return str checksum: The calculated checksum
    """
    file_hash = hashlib.sha1()
    with open(filename, 'rb') as f:
        buf = f.read()
        while len(buf) > 0:
            file_hash.update(buf)
            buf = f.read(128)
        return file_hash.hexdigest()


def file_age_in_seconds(filename):
    """
    Get the difference in seconds between now and the mtime of the file
    :param str filename: File to get the time since last mtime update of
    :return int seconds: Time in seconds since last mtime uptdate
    """
    return time() - getmtime(filename)
