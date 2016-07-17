from os import path
from fabric.context_managers import lcd
from fabric.operations import local

from raptiformica.backends.machine_config import forge_machine_config
from raptiformica.settings import DOCKER_MACHINES_DIR, PROJECT_DIR
from raptiformica.utils import generate_uuid, ensure_directory


def machine_path_from_uuid(machine_uuid):
    return path.join(DOCKER_MACHINES_DIR, machine_uuid)


def ensure_docker_image():
    dockerfile = path.join(PROJECT_DIR, 'raptiformica/backends/docker/resources/Dockerfile')
    local('cp {} .'.format(dockerfile))
    local('sudo docker build -t raptiformica-baseimage .')


def run_docker():
    return local('sudo docker run --privileged -d raptiformica-baseimage; sleep 1', capture=True)


def get_docker_ip(docker_id):
    return local('sudo docker inspect -f "{{{{ .NetworkSettings.IPAddress }}}}" {}'.format(docker_id), capture=True)


def create_new_machine_directory(new_machine_uuid):
    new_machine_path = machine_path_from_uuid(new_machine_uuid)
    ensure_directory(new_machine_path)


def create_docker_machine():
    new_machine_uuid = generate_uuid()
    create_new_machine_directory(new_machine_uuid)
    with lcd(machine_path_from_uuid(new_machine_uuid)):
        ensure_docker_image()
        docker_id = run_docker()
        local("echo {} > docker_id".format(docker_id))
        return new_machine_uuid, docker_id


def get_machine_config_from_machine_uuid(machine_uuid):
    with lcd(machine_path_from_uuid(machine_uuid)):
        docker_id = local("cat docker_id", capture=True)
        ip_address = get_docker_ip(docker_id)
        insecure_key = path.join(PROJECT_DIR, 'raptiformica/backends/docker/resources/insecure_key')
        return forge_machine_config(
                uuid=machine_uuid,
                backend='docker',
                host=ip_address,
                user='root',
                port=22,
                private_key_path=insecure_key
        )


def create_machine():
    new_machine_uuid, docker_id = create_docker_machine()
    ip_address = get_docker_ip(docker_id)
    insecure_key = path.join(PROJECT_DIR, 'raptiformica/backends/docker/resources/insecure_key')
    return forge_machine_config(
            uuid=new_machine_uuid,
            backend='docker',
            host=ip_address,
            user='root',
            port=22,
            private_key_path=insecure_key
    )
