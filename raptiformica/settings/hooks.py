from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.load import load_config, get_config_value
from raptiformica.settings.types import get_first_platform_type
from raptiformica.utils import find_key_in_dict_recursively


def gather_hook_configs(hook_name, platform_type=None):
    """
    :param str hook_name: hook to collect triggers for. e.g. 'after_mesh'
    :param str platform_type: the name of the platform type to collect
    the hooks in. defaults to the first configured type
    :return list[dict, ..]: list of hook configs
    """
    platform_type = platform_type or get_first_platform_type()
    config = load_config(MUTABLE_CONFIG)
    if platform_type not in config['platform_types']:
        raise ValueError(
            "No platform type {} in config!".format(platform_type)
        )
    platform_type_config = config['platform_types'][platform_type]
    return find_key_in_dict_recursively(platform_type_config, hook_name)


def compose_triggers_from_hook_configs(hook_configs):
    """
    Create a list of predicate and command for every item in
    the provided hook configs.
    :param list[dict, ..] hook_configs: list of hook configs
    :return list[dict, ..]: list of hooks
    """
    def get_trigger_data(hook_config):
        keys = ('predicate', 'command')
        return {v: get_config_value(hook_config, v) for v in keys}
    return map(get_trigger_data, hook_configs)


def collect_hooks(hook_name, platform_type=None):
    """
    :param str hook_name: hook to collect triggers for. e.g. 'after_mesh'
    :param str platform_type: the name of the platform type to collect
    the hooks in. defaults to the first configured type
    :return list[dict, ..]: list of hooks
    """
    platform_type = platform_type or get_first_platform_type()
    hook_configs = gather_hook_configs(
        hook_name, platform_type=platform_type
    )
    return compose_triggers_from_hook_configs(hook_configs)
