from os.path import dirname, realpath, join, expanduser

PROJECT_DIR = join(dirname(dirname(dirname(realpath(__file__)))))
INSTALL_DIR = '/usr/etc/'
RAPTIFORMICA_DIR = join(INSTALL_DIR, 'raptiformica')
CONSUL_WEB_UI_DIR = join(INSTALL_DIR, 'consul_web_ui')
CACHE_DIR = ".raptiformica.d"
ABS_CACHE_DIR = join(expanduser("~"), CACHE_DIR)
EPHEMERAL_DIR = join(ABS_CACHE_DIR, 'var')
SCRIPTS_DIR = join(PROJECT_DIR, 'scripts')
MACHINES_DIR = join(EPHEMERAL_DIR, 'machines')
BASE_CONFIG = join(PROJECT_DIR, '.base_config.json')
MUTABLE_CONFIG = join(ABS_CACHE_DIR, 'mutable_config.json')
MODULES_DIR = join(PROJECT_DIR, 'modules')
USER_MODULES_DIR = join(ABS_CACHE_DIR, 'modules')
USER_ARTIFACTS_DIR = join(ABS_CACHE_DIR, 'artifacts')
KEY_VALUE_ENDPOINT = 'http://localhost:8500/v1/kv'
KEY_VALUE_TIMEOUT = 3  # How long to wait for a config retrieval
KEY_VALUE_PATH = 'raptiformica'

CJDNS_DEFAULT_PORT = 4863
