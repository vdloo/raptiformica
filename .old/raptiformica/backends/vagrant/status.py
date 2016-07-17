from raptiformica.settings import VAGRANT_MACHINES_DIR
from raptiformica.utils import list_directories


def list_machines():
    try:
        return list_directories(VAGRANT_MACHINES_DIR)
    except OSError:
        return tuple()
