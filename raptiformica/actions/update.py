from logging import getLogger

from raptiformica.actions.slave import provision_machine
from raptiformica.settings.types import get_first_server_type

log = getLogger(__name__)


def update_machine(server_type=None):
    """
    Update the local machine by running the configured
    commands from the installed provisioning modules
    :param str server_type: name of the server type to provision the machine as
    :return:
    """
    log.info(
        "Updating local as server type {}".format(server_type)
    )
    server_type = server_type or get_first_server_type()
    provision_machine(server_type=server_type)
