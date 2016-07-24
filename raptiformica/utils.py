import json
from os import path, makedirs

from logging import getLogger

log = getLogger(__name__)


def keys_sorted(dictionary, item):
    """
    Get keys from a dictionary item and sort them
    :param dict dictionary: dictionary with an item with keys
    :param str item: name of the item to get the keys for. i.e. 'server_types'
    :return list types: list of all the types like ['headless, 'workstation']
    """
    return list(sorted(dictionary.get(item, {}).keys()))


def load_json(json_file):
    """
    Parse a json config file and return the data as a dict
    :param str json_file: path to the .json config file
    :return dict: the data from the config file
    """
    with open(json_file, 'r') as stream:
        return json.load(stream)


def ensure_directory(directory):
    """
    Create a directory if it does not exist
    :param str directory: path to the directory
    :return None:
    """
    if not path.exists(directory):
        makedirs(directory)
