from raptiformica.backends.machine_config import forge_machine_config


def create_machine():
    return forge_machine_config(backend='dryrun', host='dry_run_host')
