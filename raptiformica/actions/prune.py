from logging import getLogger
from os import listdir
from os.path import join, isdir
from shutil import rmtree

from raptiformica.settings import conf
from raptiformica.settings.load import try_delete_config, get_config
from raptiformica.settings.types import get_first_compute_type, get_first_server_type, \
    retrieve_compute_type_config_for_server_type, get_compute_types, get_server_types
from raptiformica.shell.execute import run_command_print_ready_in_directory_factory, log_failure_factory, \
    run_command_in_directory_factory

log = getLogger(__name__)


def retrieve_instance_config_items(items, default='/bin/true', server_type=None, compute_type=None):
    """
    Get the items from the instance config for the server_type as defined in the compute_type
    If no item is configured, return '/bin/true' as a noop command
    :param iterable items: List of items to retrieve
    :param mul default: default value to use if item is not found
    :param str compute_type: name of the compute type to get the server_type config for
    :param str server_type: name of the server type to get the items from
    :return tuple retrieved_items: tuple of the retrieved items
    """
    log.debug("Retrieving prune instance config")
    server_type = server_type or get_first_server_type()
    compute_type = compute_type or get_first_compute_type()
    config = retrieve_compute_type_config_for_server_type(
        server_type=server_type,
        compute_type=compute_type
    )
    return tuple([v or default for v in map(lambda k: config[k], items)])


def retrieve_prune_instance_config(server_type=None, compute_type=None):
    """
    Get the detect stale instance and clean up instance commands for the server_type as defined in the compute_type
    If no detect stale instance or clean up instance command is configured, return '/bin/true' as a noop command
    :param str compute_type: name of the compute type to start an instance on
    :param str server_type: name of the server type to provision the machine as
    :return tuple prune_instance_config: tuple of the detect_stale_instance_command
    and the clean_up_instance_command
    """
    log.debug("Retrieving prune instance config")
    return retrieve_instance_config_items(
        (
            "detect_stale_instance",
            "clean_up_instance_command"
        ),
        default='/bin/true',
        server_type=server_type,
        compute_type=compute_type
    )


def list_compute_checkouts_for_server_type_of_compute_type(server_type, compute_type):
    """
    List compute checkouts for a server type of a compute type
    :param str server_type: name of the server type to provision the machine as
    :param str compute_type: name of the compute type to start an instance on
    :return list(tuple(server_type, compute_checkout, path), ..): A list of tuples containing as the first
    item the server type, the second item the compute checkout and the third item the directory of the checkout
    """
    compute_checkouts = list()
    directories = conf().EPHEMERAL_DIR, conf().MACHINES_DIR, compute_type, \
        server_type
    server_type_of_compute_type_directory = join(*directories)
    if isdir(server_type_of_compute_type_directory):
        for compute_checkout in listdir(server_type_of_compute_type_directory):
            compute_checkouts.append(
                (server_type, compute_type,
                 join(server_type_of_compute_type_directory,
                      compute_checkout))
            )
    return compute_checkouts


def list_compute_checkouts_by_server_type_and_compute_type():
    """
    Iterate over all server types of all compute checkouts and compose a list of tuples containing as the first
    item the server type, the second item the compute checkout and the third item the directory of the checkout
    :return list(tuple(server_type, compute_checkout, path), ..): A list of tuples containing as the first
    item the server type, the second item the compute checkout and the third item the directory of the checkout
    """
    compute_checkouts = list()
    for compute_type in get_compute_types():
        for server_type in get_server_types():
            compute_checkouts.extend(
                list_compute_checkouts_for_server_type_of_compute_type(
                    server_type, compute_type
                )
            )
    return compute_checkouts


def register_clean_up_triggers(compute_checkouts):
    """
    Create a list of tuples containing an instance checkout directory and the detect stale instance and clean
    up instance commands for the specified server type of the specified compute type
    :param list(tuple(server_type, compute_checkout, path), ..) compute_checkouts: A list of tuples containing
    as the first item the server type, the second item the compute checkout and the third item the directory
    of the checkout
    :return list(tuple(directory, detect_stale_instance_command, clean_up_instance_command): List of tuples containing
    the compute checkout directory and the matching detect stale instance and clean up instance commands
    """
    triggers = list()
    clean_up_commands_cache = dict()
    for server_type, compute_type, directory in compute_checkouts:
        if (server_type, compute_type) not in clean_up_commands_cache:
            clean_up_commands_cache[(server_type, compute_type)] = tuple(
                retrieve_prune_instance_config(
                    server_type=server_type,
                    compute_type=compute_type)
            )
        detect_stale_instance_command, clean_up_instance_command = clean_up_commands_cache[
            (server_type, compute_type)
        ]
        triggers.append(
            (directory, detect_stale_instance_command, clean_up_instance_command)
        )
    return triggers


def check_if_instance_is_stale(compute_checkout_directory, detect_stale_instance_command):
    """
    Run a detect stale instance command in a compute checkout directory and return True if the instance is stale,
    return False if it is not stale
    :param str compute_checkout_directory: Directory where the local instance is bound to
    :param str detect_stale_instance_command: Command configured for the server type at the compute type that returns
    1 if the instance is stale, 0 if the instance is still active
    :return bool inactive: True if it is stale, False if it is still active
    """
    identifier = compute_checkout_directory.split('/')[-1]
    log.debug("Checking if instance bound to {} is stale".format(identifier))
    partial_run_command_print_ready = run_command_print_ready_in_directory_factory(
        compute_checkout_directory, detect_stale_instance_command
    )
    exit_code, _, _ = partial_run_command_print_ready(
        success_callback=lambda _:
        log.debug("Found active locally bound instance {}".format(identifier)),
        buffered=True
    )
    return bool(exit_code)


def clean_up_stale_instance(compute_checkout_directory, clean_up_stale_instance_command):
    """
    Run the clean up stale instance command in a compute checkout directory and clean up the checkout directory
    :param str compute_checkout_directory: Directory where the local instance is bound to
    :param str clean_up_stale_instance_command: Command configured for the server type at the compute type that
    cleans up the instance resources
    :return None:
    """
    log.info("Cleaning up stale instance in {}"
             "".format(compute_checkout_directory))
    partial_run_command = run_command_in_directory_factory(
        compute_checkout_directory, clean_up_stale_instance_command
    )
    exit_code, _, _ = partial_run_command(
        failure_callback=log_failure_factory(
            "Failed to clean up stale instance"
        ),
        buffered=True
    )


def _get_neighbour_by_key(key, value):
    """
    Get neighbours by specified key
    :param str key: The key to look for the value in
    :return list [str, ..[: : List of keys in the neighbours with the value
    for the specified key
    """
    try:
        config = get_config()
        meshnet_config = config[conf().KEY_VALUE_PATH].get('meshnet', {})
        neighbours = meshnet_config.get('neighbours', {})
        return [
            '{}/meshnet/neighbours/{}/'.format(conf().KEY_VALUE_PATH, k)
            for k, v in neighbours.items() if v[key] == value
        ]
    except KeyError as e:
        log.warning(
            "Failed to get neighbour key because "
            "of a KeyError, returning empty list: {}"
            "".format(e)
        )
        return list()


# todo: remove this function if it remains unused in the future
def get_neighbours_by_uuid(uuid):
    """
    Get neighbours by uuid
    :param str uuid: uuid of the neighbour to get the root kv store keys for
    :return list [str, ..]: List of keys of the neighbours with that uuid.
    Should only be one, but in case there are more those should also be dealt with.
    """
    return _get_neighbour_by_key('uuid', uuid)


# todo: remove this function if it remains unused in the future
def get_neighbours_by_host(host):
    """
    Get neighbours by host
    :param str host: host of the neighbour to get the root kv store keys for
    :return list [str, ..]: List of keys of the neighbours with that host.
    Should only be one, but in case there are more those should also be dealt with.
    """
    return _get_neighbour_by_key('host', host)


def _del_neighbour_by_key(key, value):
    """
    Remove a neighbour from the distributed k v mapping by key
    with a specific value.
    :param str key: The key to look for the value in
    :param str value: The value to look for
    :return None:
    """
    neighbour_keys = _get_neighbour_by_key(key, value)
    for neighbour_key in neighbour_keys:
        try_delete_config(
            neighbour_key,
            recurse=True
        )


def ensure_neighbour_removed_from_config_by_uuid(uuid):
    """
    Remove a neighbour from the distributed k v mapping by uuid
    :param str uuid: uuid of the neighbour to remove from the config
    :return None:
    """
    _del_neighbour_by_key('uuid', uuid)


def ensure_neighbour_removed_from_config_by_host(host):
    """
    Remove a neighbour from the distributed k v mapping by host
    :param str host: host of the neighbour to remove from the config
    :return None:
    """
    _del_neighbour_by_key('host', host)


def fire_clean_up_triggers(clean_up_triggers, force=False):
    """
    Fire the clean up triggers. Look for stale instances and then run the clean up instance command in
    the checkout directory for each inactive instance.
    :param list(tuple(directory, detect_stale_instance_command, clean_up_instance_command) clean_up_triggers: List
    of tuples containing the compute checkout directory and the matching detect stale instance and clean up
    instance commands
    :param bool force: Don't check if stale, always clean up
    :return None:
    """
    for directory, detect_stale_instance_command, clean_up_stale_instance_command in clean_up_triggers:
        if force or check_if_instance_is_stale(directory, detect_stale_instance_command):
            clean_up_stale_instance(directory, clean_up_stale_instance_command)
            rmtree(directory, ignore_errors=True)
            uuid = directory.split('/')[-1]
            ensure_neighbour_removed_from_config_by_uuid(uuid)


def prune_local_machines(force=False):
    """
    Remove local machines (from var/machines) that are not bound to a live instance
    :param bool force: Don't check if stale, always clean up
    :return None:
    """
    compute_checkouts = list_compute_checkouts_by_server_type_and_compute_type()
    clean_up_triggers = register_clean_up_triggers(compute_checkouts)
    fire_clean_up_triggers(clean_up_triggers, force=force)
