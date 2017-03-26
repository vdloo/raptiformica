from copy import deepcopy
from os.path import join


def get_before_slash(string):
    """
    Get the part of a string before the first slash
    :param str string: String to return the first part of
    :return str part_before_first_slash: Part of the string before
    the first slash
    """
    return string.split('/')[0]


def get_after_slash(string):
    """
    Get the part of a string after the first slash
    :param str string: String to return the part after the first
    slash of
    :return str part_after_first_slash: Part of the string after
    the first slash
    """
    return '/'.join(string.split('/')[1:])


def inflate_key_value_pair(k, v):
    """
    From a key and value, return a dict representing that key
    as a nested dictionary where the levels are determined
    by the slashes in the key path.

    Example:
    key = 'some/key', value = 'value' ->
    {'some': {'key': 'value'}}
    :param str k: key of the key value pair. If it contains
    slashes those will determined the nested levels.
    :param str v: value of the key value pair. This will be the
    deepest nested value
    :return dict nested_dict: nested dict representing the key value pair
    """
    return {
        get_before_slash(k): inflate_key_value_pair(
            get_after_slash(k), v
        )
    } if '/' in k else {k: v}


def dict_merge(first_dict, second_dict):
    """
    Merge two dicts recursively. Similar to dict.update but instead
    merge nested items instead of overwriting the entire value as soon
    as the same key is encountered. Does not mutate the dicts.

    https://gist.github.com/angstwad/bf22d1822c38a92ec0a9

    Example:
    dict 1: {'a': {'b': 1}}
    dict 2: {'a': {'c': 2}}

    Output: {'a': {'b': 1, 'c': 2}}

    Using dict.update twice would overwrite the dict 1 value 'b', this
    function builds a dict at deeper levels (Union).
    :param dict first_dict: A dict to combine with another
    :param dict second_dict: A dict to combine with another
    :return dict combined_dict: The combined dict.
    """
    def merge(dict1, dict2):
        for k, v in dict2.items():
            if k in dict1 and isinstance(dict1[k], dict):
                merge(dict1[k], dict2[k])
            else:
                dict1[k] = dict2[k]
    merged_dict = deepcopy(first_dict)
    merge(merged_dict, second_dict)
    return merged_dict


def loop_dictionary(dictionary, path='', callback=lambda path, k, v: None):
    """
    Loop the dictionary and perform the callback for each value
    :param dict dictionary: dictionary to loop for values
    :param str path: the depth in the dict joined by /
    :param func callback: the callback to perform for each value
    :return None:
    """
    for k, v in dictionary.items():
        if isinstance(v, dict):
            loop_dictionary(v, path=join(path, k), callback=callback)
        else:
            callback(path, k, v)
