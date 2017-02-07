from logging import getLogger
from pathlib import Path
from os.path import isfile

from raptiformica.settings import conf
from raptiformica.shell.execute import run_multiple_labeled_commands
from raptiformica.utils import file_age_in_seconds

log = getLogger(__name__)


def update_package_manager_cache(host=None, port=22):
    """
    Update the package manager cache
    :param str host: hostname or ip of the remote machine, None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Ensuring the package manager cache is up to date")

    ensure_cache_updated_commands = (
        ('archlinux', 'type pacman 1> /dev/null && '
                      'pacman -Syy || /bin/true'),
        ('debian', 'type apt-get 1> /dev/null && '
                   'apt-get update -yy || /bin/true')
    )
    run_multiple_labeled_commands(
        ensure_cache_updated_commands, host=host, port=port,
        failure_message="Failed to run (if {}) update package manager command"
    )


def update_local_package_manager_cache_if_necessary():
    """
    Update the package manager cache if the last update was longer than the
    specified PACKAGE_MANAGER_CACHE_OUTDATED seconds defined in the config
    :return None:
    """
    outdated = conf().PACKAGE_MANAGER_CACHE_OUTDATED
    updated = conf().PACKAGE_MANGER_UPDATED
    if not isfile(updated) or file_age_in_seconds(updated) > outdated:
        update_package_manager_cache()
        Path(updated).touch()
