from os.path import join

from consul_kv.utils import loop_dictionary, inflate_key_value_pair, dict_merge


def map_dictionary(dictionary):
    """
    Map a dictionary to key value pairs where each key is an
    accumulation of all levels of nesting for the value
    :param dict dictionary: to flatten into a k/v mapping
    :return dict mapping: key value mapping
    """
    mapping = dict()

    def add_item_to_mapping(path, k, v):
        mapping.update({join(path, k): v})

    loop_dictionary(
        dictionary,
        callback=add_item_to_mapping
    )
    return mapping


def dictionary_map(mapping):
    """
    Create a dictionary from a mapping of key value pairs where
    each key is represented by nested dicts based on slashes in
    the key path
    :param dict mapping: key value mapping
    :return dict dictionary: k/v mapping represented as a nested dict
    """
    dictionary = dict()

    def add_item_to_dictionary(path, k, v):
        dictionary.update(
            dict_merge(
                dictionary,
                inflate_key_value_pair(
                    join(path, k), v
                )
            )
        )

    loop_dictionary(
        mapping,
        callback=add_item_to_dictionary
    )

    return dictionary
