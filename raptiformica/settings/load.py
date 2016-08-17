from functools import partial
from itertools import chain

from raptiformica.settings import MODULES_DIR
from raptiformica.utils import load_json, write_json, list_all_files_with_extension_in_directory, \
    find_key_in_dict_recursively, transform_key_in_dict_recursively

from logging import getLogger

log = getLogger(__name__)


def load_config(config_file):
    """
    Load a config file or default to the base config
    :param str config_file: path to the .json config file
    :return dict: the config data
    """
    try:
        return load_json(config_file)
    except (OSError, ValueError):
        log.warning("Failed loading config file. Falling back to base config")
        config = load_modules(modules_dir=MODULES_DIR)
        if not config:
            raise ValueError("No valid config available")
        write_config(config, config_file)
        return config


def write_config(config, config_file):
    """
    Write the config to a config file
    :param dict config: The config to be dumped to json
    :param str config_file: The mutable config file
    :return None:
    """
    write_json(config, config_file)


def load_module_configs(modules_dir=MODULES_DIR):
    """
    Find all configuration files in the modules_dir and return them as parsed a list
    :param str modules_dir: path to look for .json config files in
    :return list configs: list of parsed configs
    """
    file_names = list_all_files_with_extension_in_directory(
        modules_dir, 'json'
    )

    def try_load_module(filename):
        try:
            return load_json(filename)
        except ValueError:
            log.warning("Failed to parse module config in {}, "
                        "skipping..".format(filename))
    configs = filter(lambda x: x is not None, map(try_load_module, file_names))
    # cast to list because the result of this function is likely to be
    # iterated multiple times
    return list(configs)


def find_key_in_module_configs_recursively(configs, key_to_find):
    """
    Find a key in a list of dicts recursively and return the matching values
    in a list.
    :param list[dict, ..] configs: list of config dictionaries
    :param str key_to_find: the key to look for recursively in all dicts
    :return list values: list of values matching the key in the configs
    """
    return map(partial(find_key_in_dict_recursively, key_to_find=key_to_find), configs)


def merge_module_configs(configs):
    """
    Take a list of dicts and merge them into one dict.
    Later keys overwrite previous previously defined keys.
    :param list[dict, ..] configs: list of config dictionaries
    :return dict merged_config: the merged config
    """

    return {k: v for i in map(lambda c: c.items(), configs) for k, v in i}


def merge_module_types(configs):
    """
    Take a list of type configs and merges the module configs after flattening the list.
    :param list[dict, ..] configs: list of config dictionaries
    :return dict merged_config: the merged config
    """
    return merge_module_configs(chain.from_iterable(configs))


def compose_module_prototypes(configs):
    """
    Gather all prototypes in a list of configs dictionaries recursively
    and merge them flattened into a dictionary.
    :param list[dict, ..] configs: list of config dictionaries
    :return dict module_prototypes: dict of module prototypes
    """
    module_prototypes = find_key_in_module_configs_recursively(
        configs, 'module_prototype'
    )
    return merge_module_types(module_prototypes)


def resolve_prototypes(prototypes, config):
    """
    Iteratively loop over a config and resolve prototype keys recursively
    from the passed prototypes directory. Will raise a RuntimeError if an
    encountered prototype can not be resolved.
    :param dict prototypes: dict of module prototypes
    :param dict config: config to resolve the prototypes in recursively
    (if a resolved prototype contains a prototype that prototype will also
    be resolved)
    :return dict resolved_config: the config with all prototypes resolved.
    """
    def resolve_prototype(_, value):
        if not isinstance(value, str):
            return value
        if value not in prototypes:
            raise RuntimeError("Missing prototype {}".format(value))
        return resolve_prototypes(prototypes, prototypes[value])
    return transform_key_in_dict_recursively(
        config, 'prototype', resolve_prototype
    )


def compose_types(prototypes, configs, types_name):
    """
    Compose a types configuration of name types_name based on the config provided.
    Resolves encountered module_prototypes using the passed prototypes dictionary.
    :param dict prototypes: dict of module prototypes
    :param list[dict, ..] configs: list of config dictionaries
    :param str types_name: name of the type to compose
    :return dict resolved_config: the config with all prototypes resolved.
    """
    compute_types = list(
        find_key_in_module_configs_recursively(configs, types_name)
    )
    merged = merge_module_types(compute_types)
    return resolve_prototypes(prototypes, merged)


def load_modules(modules_dir=MODULES_DIR):
    """
    Construct the mutable_config from the module configuration files on disk.
    :param str modules_dir: path to look for .json config files in
    :return dict: mutable_config
    """
    configs = load_module_configs(modules_dir=modules_dir)
    prototypes = compose_module_prototypes(configs)
    modules = list(chain.from_iterable(
        find_key_in_module_configs_recursively(configs, 'module_name'))
    )
    return {m: compose_types(prototypes, configs, m) for m in modules}


def get_config_value(config, item_name, default=''):
    """
    Compose a config value based for key item_name based on the config
    passed by traversing up the prototype tree if necessary. Returns
    default if no matching value was encountered. The default value
    must have + implemented.

    :param dict config: a module config to look for the item_name key in
    :param str item_name: item name to look for in config
    :param mul default: a value of a type that has + implemented. e.g. '' as a string
    :return mul: the constructed config value
    """
    # filter out prototypes from the config dict so we search by
    # breadth first instead of depth first
    flat_config = transform_key_in_dict_recursively(
        dict(config), 'prototype', lambda k, v: {}
    )
    values = find_key_in_dict_recursively(flat_config, item_name) or [
        {'content': default}
    ]
    for value in values:
        try:
            if not value['content'] or value.get('append_prototype_content'):
                value['content'] += get_config_value(
                    config['prototype'],
                    item_name
                ) or default
            return value['content']
        except (KeyError, TypeError):
            continue
    return default
