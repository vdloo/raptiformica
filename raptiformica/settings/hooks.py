from os.path import join
from raptiformica.settings import KEY_VALUE_PATH
from raptiformica.settings.load import get_config
from raptiformica.settings.types import get_first_platform_type
from raptiformica.utils import startswith


def collect_hooks(hook_name, platform_type=None):
    """
    :param str hook_name: hook to collect triggers for. e.g. 'after_mesh'
    :param str platform_type: the name of the platform type to collect
    the hooks in. defaults to the first configured type
    :return iterable[dict, ..]: list of hooks
    """
    platform_type = platform_type or get_first_platform_type()
    mapped = get_config()
    hook_path = '{}/platform/{}/hooks/{}/'.format(
        KEY_VALUE_PATH, platform_type, hook_name
    )
    hook_keys = set(map(
        lambda x: '/'.join(x.split('/')[:-1]),
        filter(
            startswith(hook_path),
            mapped
        )
    ))
    return map(
        lambda x: {
            'predicate': mapped.get(join(x, 'predicate'), '/bin/true'),
            'command': mapped.get(join(x, 'command'), '/bin/true')
        },
        hook_keys
    )
