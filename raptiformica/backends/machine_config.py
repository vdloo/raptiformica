from raptiformica.utils import generate_uuid


def forge_machine_config(uuid=None, backend=None, host=None, user='root', port=22, private_key_path=None):
    uuid = uuid or generate_uuid()
    return {
        'Backend': backend,
        'HostName': host,
        'IdentityFile': private_key_path,
        'Port': port,
        'User': user,
        'Uuid': uuid,
    }


def ssh_command_from_machine_config(machine_config):
    cmd = "ssh -oStrictHostKeyChecking=no {User}@{HostName}".format(**machine_config)
    if machine_config['Port'] and machine_config['Port'] != 22:
        cmd += ' -p {}'.format(machine_config['Port'])
    if machine_config['IdentityFile']:
        cmd += ' -i "{}"'.format(machine_config['IdentityFile'])
    return cmd
