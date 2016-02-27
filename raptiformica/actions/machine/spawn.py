from logging import getLogger

from raptiformica.backends.machine_config import ssh_command_from_machine_config
from raptiformica.backends.resolve import resolve_manage_machine

log = getLogger(__name__)


def spawn_machine(backend_name):
    log.info('Spawning machine using the {} backend'.format(backend_name))

    backend = resolve_manage_machine(backend_name)
    machine_config = backend.create_machine()

    log.info("Spawned new machine, uuid is {}".format(machine_config['Uuid']))
    log.info("For ssh access:\n  {}".format(ssh_command_from_machine_config(machine_config)))

    return machine_config
