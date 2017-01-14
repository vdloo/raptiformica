from raptiformica.settings import conf
from raptiformica.settings.load import get_config
from raptiformica.settings.types import get_first_platform_type


def collect_hooks(hook_name, platform_type=None):
    """
    :param str hook_name: hook to collect triggers for. e.g. 'after_mesh'
    :param str platform_type: the name of the platform type to collect
    the hooks in. defaults to the first configured type
    :return iterable[dict, ..]: list of hooks
    """
    platform_type = platform_type or get_first_platform_type()
    config = get_config()
    platform = config[conf().KEY_VALUE_PATH]['platform'][platform_type]
    hooks = platform.get('hooks', {}).get(hook_name, {})
    return [{k: hook.get(k, '/bin/true') for k in ('predicate', 'command')}
            for hook in hooks.values()]
