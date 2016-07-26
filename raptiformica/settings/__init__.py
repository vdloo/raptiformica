from os.path import dirname, realpath, join

PROJECT_DIR = join(dirname(dirname(dirname(realpath(__file__)))))
INSTALL_DIR = '/usr/etc/'
RAPTIFORMICA_DIR = join(INSTALL_DIR, 'raptiformica')
EPHEMERAL_DIR = join(PROJECT_DIR, 'var')
SCRIPTS_DIR = join(PROJECT_DIR, 'scripts')
MACHINES_DIR = join(EPHEMERAL_DIR, 'machines')
BASE_CONFIG = join(PROJECT_DIR, 'base_config.json')
