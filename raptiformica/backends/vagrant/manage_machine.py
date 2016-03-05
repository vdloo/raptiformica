from os import path
from fabric.api import lcd, local

from raptiformica.backends.machine_config import forge_machine_config
from raptiformica.settings import VAGRANT_FILES_REPOSITORY, VAGRANT_FILES_SUBDIRECTORY, VAGRANT_MACHINES_DIR
from raptiformica.utils import ensure_directory, generate_uuid


def machine_path_from_uuid(machine_uuid):
    return path.join(VAGRANT_MACHINES_DIR, machine_uuid)


def vagrant_path_from_uuid(machine_uuid):
    machine_path = machine_path_from_uuid(machine_uuid)
    return path.join(machine_path, VAGRANT_FILES_SUBDIRECTORY)


def create_new_machine_directory(new_machine_uuid):
    new_machine_path = machine_path_from_uuid(new_machine_uuid)
    ensure_directory(new_machine_path)


def ensure_vagrant_files():
    local('git clone {}'.format(VAGRANT_FILES_REPOSITORY))


def create_vagrant_machine():
    new_machine_uuid = generate_uuid()
    create_new_machine_directory(new_machine_uuid)
    with lcd(machine_path_from_uuid(new_machine_uuid)):
        ensure_vagrant_files()
        with lcd(VAGRANT_FILES_SUBDIRECTORY):
            local("vagrant up")
    return new_machine_uuid


def ensure_machine_booted(machine_uuid):
    with lcd(machine_path_from_uuid(machine_uuid)):
        with lcd(VAGRANT_FILES_SUBDIRECTORY):
            local("vagrant up", capture=True)


def parse_vagrant_config(ssh_config_output):
    vagrant_config_list = map(lambda l: l.strip().split(' '), ssh_config_output.splitlines())
    vagrant_config = {i[0]: ' '.join(i[1:]).strip("\"") for i in vagrant_config_list}
    return vagrant_config


def get_vagrant_config(vagrant_path):
    with lcd(vagrant_path):
        ssh_config_output = local("vagrant ssh-config", capture=True)
        return parse_vagrant_config(ssh_config_output)


def vagrant_config_to_machine_config(machine_uuid, vagrant_config):
    return forge_machine_config(
            uuid=machine_uuid,
            backend='Vagrant',
            host=vagrant_config['HostName'],
            user=vagrant_config['User'],
            port=vagrant_config['Port'],
            private_key_path=vagrant_config['IdentityFile']
    )


def get_machine_config_from_machine_uuid(machine_uuid):
    ensure_machine_booted(machine_uuid)
    vagrant_path = vagrant_path_from_uuid(machine_uuid)
    vagrant_config = get_vagrant_config(vagrant_path)
    return vagrant_config_to_machine_config(machine_uuid, vagrant_config)


def create_machine():
    new_machine_uuid = create_vagrant_machine()
    return get_machine_config_from_machine_uuid(new_machine_uuid)
