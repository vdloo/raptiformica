from fabric.operations import local

from raptiformica.backends.machine_config import ssh_command_from_machine_config


def ssh(machine_config):
    ssh_command = ssh_command_from_machine_config(machine_config)
    local(ssh_command)