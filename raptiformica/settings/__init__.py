from os.path import dirname, realpath, join

PROJECT_DIR = join(dirname(dirname(dirname(realpath(__file__)))))
INSTALL_DIR = '/usr/etc/'
EPHEMERAL_DIR = join(PROJECT_DIR, 'var')
MACHINES_DIR = join(EPHEMERAL_DIR, 'machines')
BASE_CONFIG = join(PROJECT_DIR, 'base_config.json')
