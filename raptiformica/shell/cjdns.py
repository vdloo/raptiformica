from os import path
from logging import getLogger

from raptiformica.settings import INSTALL_DIR, SCRIPTS_DIR, RAPTIFORMICA_DIR
from raptiformica.shell.execute import raise_failure_factory, run_command_remotely_print_ready
from raptiformica.shell.git import ensure_latest_source

CJDNS_REPOSITORY = "https://github.com/cjdelisle/cjdns.git"

log = getLogger(__name__)


def ensure_cjdns_dependencies(host, port=22):
    """
    Install CJDNS dependencies. Each command in the loop should check for identifiers of a
    certain distro and then run the idempotent install command if that distro is detected.
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Ensuring the CJDNS dependencies are installed")

    ensure_cjdns_dependencies_commands = (
        ('archlinux', '"type -p pacman 1> /dev/null && '
                      'pacman -S --noconfirm nodejs base-devel --needed || /bin/true"'),
        ('debian', '"type -p apt-get 1> /dev/null && '
                   '(apt-get update -yy && '
                   'apt-get install -yy nodejs '
                   'build-essential git python) || /bin/true"')
    )
    for d, command_as_string in ensure_cjdns_dependencies_commands:
        run_command_remotely_print_ready(
            ["sh", "-c", command_as_string],
            host, port=port,
            failure_callback=raise_failure_factory(
                "Failed to run (if {}) install cjdns "
                "dependencies command".format(d)
            ),
            buffered=False
        )


def cjdns_setup(host, port=22):
    """
    Build cjdns. This is done with scripts because at this point in the code no guarantees can be made
    about the remote host's environment. Each command in the loop should check for identifiers of a certain
    distro and then run the idempotent install command if that distro is detected.
    :param str host: hostname or ip of the remote machine
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
    exit_code, _, _ = run_command_remotely_print_ready(
        cjdns_setup_command,
        host, port=port,
        failure_callback=raise_failure_factory(
            "Failed to ensure that CJDNS was built, configured and installed"
        ),
        buffered=False
    )
    return exit_code


def ensure_cjdns_installed(host, port=22):
    """
    Install cjdns. This is done with scripting instead of puppet for ansible because at this point in the code
    no guarantees can be made about the remote host's environment.
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Ensuring CJDNS is installed")
    ensure_latest_source(CJDNS_REPOSITORY, "cjdns", host, port=port)
    ensure_cjdns_dependencies(host, port=port)
    cjdns_setup(host, port=port)
