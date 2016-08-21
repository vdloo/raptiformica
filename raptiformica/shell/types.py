from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.load import load_config, get_config_value
from raptiformica.shell.execute import run_command_print_ready

cached_available = {}


def evaluate_available(item, type_name, predicate):
    """
    Run the check_available predicate and cache the result.
    If there is already a cached result, use that and don't
    run the predicate command.
    :param str item: name of the item to check the type for. i.e. 'server_types
    :param str type_name: name of the type. i.e. 'headless'
    :param str predicate: the check_available command
    :return bool type_available: whether or not the type is available
    """
    global cached_available
    if (item, type_name) not in cached_available:
        exit_code, _, _ = run_command_print_ready(
            shell=True,
            command=predicate
        )
        cached_available[(item, type_name)] = exit_code == 0
    return cached_available[(item, type_name)]


def check_type_available(item, type_name):
    """
    Check if the type for the config item is available on
    this machine if a check_available predicate exists, otherwise
    return True because there are no requirements configured for
    the type and we assume it is available.
    :param str item: name of the item to check the type for. i.e. 'server_types
    :param str type_name: name of the type. i.e. 'headless'
    :return bool type_available: whether or not the type is available
    """
    config = load_config(MUTABLE_CONFIG)
    type_config = config[item][type_name]
    predicate = get_config_value(type_config, "check_available_command")
    print(predicate)
    if predicate:
        return evaluate_available(
            item, type_name, predicate
        ) if predicate else True
    else:
        return True
