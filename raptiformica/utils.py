import json
from functools import partial
from itertools import chain
from os import path, makedirs, walk

from logging import getLogger

from collections import Iterable

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


def transform_key_in_dict_recursively(dictionary, key_to_find, transformer=lambda k, v: v):
    """
    Find every occurrence of a specific key in a directory and transform the value with the transformer function and
    return the mutated dict
    Note: mutates the passed dictionary and returns it. Wrap argument in dict() to not mutate the original.
    :param dict dictionary: the dictionary to look in
    :param str key_to_find: the key to look for
    :param func transformer: function to mutate the value with. takes the key and value as arguments.
    defaults to identity function
    :return dict dictionary: the mutated dictionary
    """
    for key, value in dictionary.items():
        if key == key_to_find:
            dictionary[key] = transformer(key, value)
        elif isinstance(value, dict):
            dictionary[key] = transform_key_in_dict_recursively(
                value, key_to_find, transformer=transformer
            )
        elif isinstance(value, Iterable) and not isinstance(value, str):
            dictionary[key] = list(chain.from_iterable(
                map(
                    partial(
                        transform_key_in_dict_recursively,
                        key_to_find=key_to_find,
                        transformer=transformer
                    ),
                    value
                )
            ))
    return dictionary


def find_key_in_dict_recursively(dictionary, key_to_find):
    """
    Find every occurrence of a specific key in a dictionary recursively and return a list of the found values
    :param dict dictionary: the dictionary to look in
    :param str key_to_find: the key to look for
    :return list[dict, ..]: list with the found dicts
    """
    found = list()
    for key, value in dictionary.items():
        if key == key_to_find:
            found.append(value)
        elif isinstance(value, dict):  # I wish python had a macro system
            found.extend(
                find_key_in_dict_recursively(value, key_to_find)
            )
        elif isinstance(value, Iterable) and not isinstance(value, str):
            found.extend(
                chain.from_iterable(
                    map(
                        partial(
                            find_key_in_dict_recursively,
                            key_to_find=key_to_find
                        ),
                        value
                    )
                )
            )
    return found
