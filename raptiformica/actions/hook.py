from logging import getLogger

from raptiformica.shell.hooks import fire_hooks

log = getLogger(__name__)


def trigger_handlers(hook_name):
    """
    Trigger the handlers of a specific hook
    :param hook_name:
    :return:
    """
    log.info("Triggering handlers found for hook '{}'".format(hook_name))
    amount = fire_hooks(hook_name)
    log.info("Fired {} hooks.".format(amount))
