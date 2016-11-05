from logging import getLogger

from raptiformica.settings import KEY_VALUE_PATH
from raptiformica.settings.load import get_config
from raptiformica.settings.types import get_first_server_type, get_first_compute_type
from raptiformica.shell.execute import run_command

log = getLogger(__name__)


def retrieve_package_machine_config(server_type=None, compute_type=None):
    """
    Get the package command from the server_type as defined in the compute_type
    :param str compute_type: name of the compute type to start an instance on
    :param str server_type: name of the server type to provision the machine as
    :return str package_command: The package command
    """
    server_type = server_type or get_first_server_type()
    compute_type = compute_type or get_first_compute_type()
    config = get_config()
    server_config = config[KEY_VALUE_PATH][
        'compute'
    ][compute_type].get(server_type, {})
    if 'package' not in server_config:
        raise RuntimeError("No packaging command specified for "
                           "server type {} of compute type {}"
                           "".format(server_type, compute_type))
    return server_config['package']


def package_machine(server_type=None, compute_type=None, only_check_available=False):
    """
    Package a machine into a reusable image for the compute provider
    :param str server_type: name of the server type to provision the machine as
    :param str compute_type: name of the compute type to start an instance on
    :param bool only_check_available: Don't really spawn a machine, just check if this host could
    :return:
    """
    server_type = server_type or get_first_server_type()
    compute_type = compute_type or get_first_compute_type()
    # If we are just checking for availability we are done here
    if not only_check_available:
        log.info(
            "Packaging machine of server type {} with compute "
            "type {}".format(server_type, compute_type)
        )
        package_command = retrieve_package_machine_config(
            server_type=server_type, compute_type=compute_type
        )
        run_command(package_command, buffered=False, shell=True)
