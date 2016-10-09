from os import path
from logging import getLogger

from raptiformica.settings import INSTALL_DIR, RAPTIFORMICA_DIR
from raptiformica.shell.execute import raise_failure_factory, \
    run_critical_unbuffered_command_print_ready, run_command_print_ready, \
    run_multiple_labeled_commands
from raptiformica.shell.git import ensure_latest_source

CJDNS_REPOSITORY = "https://github.com/cjdelisle/cjdns.git"

log = getLogger(__name__)


def get_cjdns_config_item(item, host=None, port=22):
    """
    Retrieve an item from the cjdroute.conf on a remote machine.
    :param str item: which item from the cjdroute.conf json to get
    :param str host: hostname or ip of the remote machine, None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return str: the item as string
    """
    get_config_item_command = [
        'sh', '-c',
        '"cat /etc/cjdroute.conf | '
        # todo: refactor this hideous hack. want to keep it without
        # dependencies though.
        'python -c \\"import sys, json; '
        'print(json.load(sys.stdin)[\'{}\'])\\""'.format(item)
    ]
    _, standard_out, _ = run_command_print_ready(
        get_config_item_command, host=host, port=port,
        failure_callback=raise_failure_factory(
            "Failed to retrieve CJDNS {} "
            "from {}".format(item, host)
        )
    )
    return standard_out.strip()


def get_public_key(host=None, port=22):
    """
    Get the generated public key from a remote host
    :param str host: hostname or ip of the remote machine, or None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return str public_key: The CJDNS public key from the remote host`
    """
    log.info("Getting the CJDNS public key from {}".format(
        host or 'the local host'
    ))
    return get_cjdns_config_item('publicKey', host=host, port=port)


def get_ipv6_address(host=None, port=22):
    """
    Get the generated ipv6 address from a remote host
    :param str host: hostname or ip of the remote machine, None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return str address: The CJDNS ipv6 address from the remote host`
    """
    log.info("Getting the CJDNS ipv6 address from {}".format(
        host or 'the local host')
    )
    return get_cjdns_config_item('ipv6', host=host, port=port)


def ensure_cjdns_dependencies(host=None, port=22):
    """
    Install CJDNS dependencies. Each command in the loop should check for identifiers of a
    certain distro and then run the idempotent install command if that distro is detected.
    :param str host: hostname or ip of the remote machine, None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Ensuring the CJDNS dependencies are installed")

    ensure_cjdns_dependencies_commands = (
        ('archlinux', 'type pacman 1> /dev/null && '
                      'pacman -S --noconfirm nodejs base-devel --needed || /bin/true'),
        ('debian', 'type apt-get 1> /dev/null && '
                   '(apt-get update -yy && '
                   'apt-get install -yy nodejs '
                   'build-essential git python) || /bin/true')
    )
    run_multiple_labeled_commands(
        ensure_cjdns_dependencies_commands, host=host, port=port,
        failure_message="Failed to run (if {}) install cjdns "
                        "dependencies command"
    )


def cjdns_setup(host=None, port=22):
    """
    Build cjdns. This is done with scripts because at this point in the code no guarantees can be made
    about the remote host's environment. Each command in the loop should check for identifiers of a certain
    distro and then run the idempotent install command if that distro is detected.
    :param str host: hostname or ip of the remote machine, None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return int exit_code: exit code of the configured bootstrap command
    """
    log.info("Build, configure and install CJDNS")
    cjdns_checkout_directory = path.join(INSTALL_DIR, 'cjdns')
    setup_script = path.join(RAPTIFORMICA_DIR, 'resources/setup_cjdns.sh')
    cjdns_setup_command = [
        'bash', '-c', 'cd {} && {}'.format(
            cjdns_checkout_directory, setup_script,
        )
    ]
    exit_code, _, _ = run_critical_unbuffered_command_print_ready(
        cjdns_setup_command, host=host, port=port,
        failure_message="Failed to ensure that CJDNS was built, "
                        "configured and installed"
    )
    return exit_code


def ensure_cjdns_installed(host=None, port=22):
    """
    Install cjdns. This is done with scripting instead of puppet for ansible because at this point in the code
    no guarantees can be made about the remote host's environment.
    :param str host: hostname or ip of the remote machine, None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Ensuring CJDNS is installed")
    ensure_latest_source(CJDNS_REPOSITORY, "cjdns", host=host, port=port)
    ensure_cjdns_dependencies(host=host, port=port)
    cjdns_setup(host=host, port=port)
