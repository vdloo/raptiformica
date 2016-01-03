import os
from fabric.api import lcd, local

from raptiformica.settings import PROJECT_DIR, VAGRANT_FILES_SUBDIRECTORY

SCRIPTS_DIR = os.path.join(PROJECT_DIR, 'scripts')


def get_vagrant_config():
    ssh_config_output = local("vagrant ssh-config", capture=True)
    return parse_vagrant_config(ssh_config_output)


def parse_vagrant_config(ssh_config_output):
    ssh_config_list = map(lambda l: l.strip().split(' '), ssh_config_output.splitlines())
    ssh_config = {i[0]: ' '.join(i[1:]) for i in ssh_config_list}
    return ssh_config


def upload_scripts(ssh_config):
    local("rsync -avz -e \"ssh -p %s -i %s -o StrictHostKeyChecking=no\" \"%s\" %s@%s:/tmp --progress" %
          (ssh_config['Port'], ssh_config['IdentityFile'], SCRIPTS_DIR, ssh_config['User'], ssh_config['HostName']))


def install_cjdns(ssh_config):
    local('ssh -p %s -i %s -o StrictHostKeyChecking=no %s@%s "(cd /tmp/scripts; sudo bash install_cjdns.sh)"' %
          (ssh_config['Port'], ssh_config['IdentityFile'], ssh_config['User'], ssh_config['HostName']))


def slave_machine(new_machine_vagrant_directory):
    with lcd(new_machine_vagrant_directory):
        ssh_config = get_vagrant_config()
        upload_scripts(ssh_config)
        install_cjdns(ssh_config)
