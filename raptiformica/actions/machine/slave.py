from fabric.api import local
from logging import getLogger

from raptiformica.settings import SCRIPTS_DIR

log = getLogger(__name__)


def get_vagrant_config():
    machine_config_output = local("vagrant ssh-config", capture=True)
    return parse_vagrant_config(machine_config_output)


def parse_vagrant_config(machine_config_output):
    machine_config_list = map(lambda l: l.strip().split(' '), machine_config_output.splitlines())
    machine_config = {i[0]: ' '.join(i[1:]) for i in machine_config_list}
    return machine_config


def upload_scripts(machine_config):
    log.info("Uploading scripts")
    if machine_config['Backend'] != 'dryrun':
        local("rsync -avz -e \"ssh -p %s -i %s -o StrictHostKeyChecking=no\" \"%s\" %s@%s:/tmp --progress" %
              (machine_config['Port'], machine_config['IdentityFile'], SCRIPTS_DIR, machine_config['User'], machine_config['HostName']))


def install_cjdns(machine_config):
    log.info("Installing cjdns")
    if machine_config['Backend'] != 'dryrun':
        local('ssh -p %s -i %s -o StrictHostKeyChecking=no %s@%s "(cd /tmp/scripts; '
              'sudo bash install_cjdns.sh; '
              'sudo bash var/bootstrap_cjdns.sh; '
              'sudo bash install_consul.sh)"' %
              (machine_config['Port'], machine_config['IdentityFile'], machine_config['User'], machine_config['HostName']))


def slave_machine(machine_config):
    log.info("Slaving machine")
    upload_scripts(machine_config)
    install_cjdns(machine_config)
    log.info("Slaved machine")
