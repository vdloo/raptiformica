import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SCRIPTS_DIR = os.path.join(PROJECT_DIR, 'scripts')
MACHINES_DIR = os.path.join(PROJECT_DIR, 'machines')

VAGRANT_MACHINES_DIR = os.path.join(MACHINES_DIR, 'vagrant')
VAGRANT_FILES_REPOSITORY = 'https://github.com/vdloo/vagrantfiles'
VAGRANT_FILES_SUBDIRECTORY = 'vagrantfiles/headless'

DOCKER_MACHINES_DIR = os.path.join(MACHINES_DIR, 'docker')

INSTANCE_BACKEND_DEFAULT = 'vagrant'
LOCAL_BACKENDS = ('vagrant', 'docker', 'dryrun')
REMOTE_BACKENDS = tuple()

