import os
from fabric.api import lcd, local

from raptiformica.settings import PROJECT_DIR, VAGRANT_FILES_REPOSITORY, VAGRANT_FILES_SUBDIRECTORY
from raptiformica.utils import ensure_directory, generate_uuid

MACHINES_DIR = os.path.join(PROJECT_DIR, 'machines')


def create_new_machine_directory():
    new_machine_uuid = generate_uuid()
    new_machine_dir = os.path.join(MACHINES_DIR, new_machine_uuid)
    ensure_directory(new_machine_dir)
    return new_machine_dir


def ensure_vagrant_files():
    local('git clone %s' % VAGRANT_FILES_REPOSITORY)
    return VAGRANT_FILES_SUBDIRECTORY


def spawn_machine():
    new_machine_directory = create_new_machine_directory()
    with lcd(new_machine_directory):
        vagrant_directory = ensure_vagrant_files()
        with lcd(vagrant_directory):
            local("vagrant up")
    return os.path.join(new_machine_directory, vagrant_directory)
