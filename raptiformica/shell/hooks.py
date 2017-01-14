from logging import getLogger

from raptiformica.settings import conf
from raptiformica.settings.hooks import collect_hooks
from raptiformica.settings.types import get_first_platform_type
from raptiformica.shell.execute import log_failure_factory, run_command_in_directory_factory

log = getLogger(__name__)


def fire_hook(hook):
    """
    Fire a hook. Run the 'command' command in the dict if the
    'predicate' command in the dict evaluates to a zero exit
    code.
    :param dict hook: dict containing a predicate and command
    :return None:
    """
    log.debug("Firing hook..")
    run_predicate_print_ready = run_command_in_directory_factory(
        conf().RAPTIFORMICA_DIR, hook['predicate']
    )
    exit_code, _, _ = run_predicate_print_ready()
    if exit_code == 0:
        run_command_in_directory_partial = run_command_in_directory_factory(
            conf().RAPTIFORMICA_DIR, hook['command']
        )
        run_command_in_directory_partial(
            buffered=False,
            failure_callback=log_failure_factory(
                "Failed firing hook. That is probably not the end "
                "of the world. Continuing.."
            )
        )


def fire_hooks(hook_name, platform_type=None):
    """
    Fire all hooks for hook_name. Will run the predicate for each hook
    and if it returns a zero exit code it will run the matching command.
    :param str hook_name: hook to collect triggers for. e.g. 'after_mesh'
    :param str platform_type: the name of the platform type to collect
    the hooks in. defaults to the first configured type
    :return int amount: the amount of hooks found and fired
    """
    log.info("Gathering hooks for {}".format(hook_name))
    platform_type = platform_type or get_first_platform_type()
    hooks = list(collect_hooks(hook_name, platform_type=platform_type))
    for hook in hooks:
        fire_hook(hook)
    return len(hooks)
