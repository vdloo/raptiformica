from logging import getLogger

from raptiformica.actions.machine.list import set_of_all_machines_on_all_backends, \
    list_of_all_machine_configs_on_all_backends
from raptiformica.backends.machine_config import ssh_command_from_machine_config
from raptiformica.utils import pretty_dump

log = getLogger(__name__)


def show_config(machine_config):
    log.info(pretty_dump(machine_config))


def show_ssh_command(machine_config):
    log.info("Log in:\n{}".format(ssh_command_from_machine_config(machine_config)))


def show(machine_config):
    log.info("Displaying information about machine {}".format(machine_config['Uuid']))
    show_config(machine_config)
    show_ssh_command(machine_config)


def show_all():
    map(show_config, list_of_all_machine_configs_on_all_backends())
