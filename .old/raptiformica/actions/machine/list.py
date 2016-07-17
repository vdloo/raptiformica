from logging import getLogger
from itertools import chain

from raptiformica.backends.resolve import resolve_status, resolve_manage_machine
from raptiformica.settings import LOCAL_BACKENDS, REMOTE_BACKENDS
from raptiformica.utils import pretty_dump

log = getLogger(__name__)


def set_of_all_machines_on_backends(backends):
    """
    Return a set of all machines on the provided backends
    :param list(str backend, ..) backends: iterable of backend names
    :return:
    """
    return set(chain.from_iterable([status.list_machines() for status in map(resolve_status, backends)]))


def set_of_all_machines_on_all_backends():
    return set_of_all_machines_on_backends(LOCAL_BACKENDS) | set_of_all_machines_on_backends(REMOTE_BACKENDS)


def list_of_all_machine_configs_on_all_backends():
    backends = LOCAL_BACKENDS
    return chain.from_iterable(map(lambda backend: map(lambda machine_uuid: resolve_manage_machine(backend).get_machine_config_from_machine_uuid(machine_uuid),
               list(set_of_all_machines_on_backends([backend]))), backends))


def list_local():
    log.info("Listing all local machines")
    machines = list(set_of_all_machines_on_backends(LOCAL_BACKENDS))
    log.info(pretty_dump(machines, empty_message='No local machines'))


def list_remote():
    log.info("Listing all remote machines")
    # TODO: add remote backends
    machines = list(set_of_all_machines_on_backends(REMOTE_BACKENDS))
    log.info(pretty_dump(machines, empty_message='No remote machines'))


def list_all():
    log.info("Listing all known machines")
    machines = list(set_of_all_machines_on_all_backends())
    log.info(pretty_dump(machines, empty_message='No machines'))
