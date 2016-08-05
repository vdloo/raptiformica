from os import path
from logging import getLogger

from raptiformica.settings import RAPTIFORMICA_DIR
from raptiformica.shell.execute import run_critical_unbuffered_command_remotely_print_ready, \
    run_remote_multiple_labeled_commands

log = getLogger(__name__)

CONSUL_RELEASE = 'https://releases.hashicorp.com/consul/0.6.4/consul_0.6.4_linux_amd64.zip'


def ensure_consul_dependencies(host, port=22):
    """
    Install consul dependencies. Each command in the loop should check for identifiers of a
    certain distro and then run the idempotent install command if that distro is detected.
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Ensuring the consul dependencies are installed")

    ensure_consul_dependencies_commands = (
        ('archlinux', '"type pacman 1> /dev/null && '
                      'pacman -S --noconfirm wget unzip screen --needed || /bin/true"'),
        ('debian', '"type apt-get 1> /dev/null && '
                   '(apt-get update -yy && '
                   'apt-get install -yy wget unzip screen) || /bin/true"')
    )
    run_remote_multiple_labeled_commands(
        ensure_consul_dependencies_commands, host, port=port,
        failure_message="Failed to run (if {}) install consul "
                        "dependencies command"
    )


def ensure_latest_consul_release(host, port=22):
    """
    Make sure the latest consul release is downloaded on the remote machine
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Ensuring consul release {} is on disk "
             "on the remote machine".format(CONSUL_RELEASE.split('/')[-1]))
    run_critical_unbuffered_command_remotely_print_ready(
        ['wget', '-nc', CONSUL_RELEASE], host, port=port,
        failure_message="Failed to retrieve latest consul release"
    )


def unzip_consul_release(host, port=22):
    """
    Unzip the consul binary to /usr/bin
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Making sure the consul binary is placed in /usr/bin")
    run_critical_unbuffered_command_remotely_print_ready(
        ['unzip', '-o', CONSUL_RELEASE.split('/')[-1], '-d', '/usr/bin'],
        host, port=port, failure_message="Failed to retrieve latest consul release"
    )


def consul_setup(host, port=22):
    """
    Run the consul setup script. Places the systemd service file.
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return int exit_code: exit code of the configured bootstrap command
    """
    log.info("Build, configure and install CJDNS")
    setup_script = path.join(RAPTIFORMICA_DIR, 'resources/setup_consul.sh')
    cjdns_setup_command = [setup_script]
    exit_code, _, _ = run_critical_unbuffered_command_remotely_print_ready(
        cjdns_setup_command, host, port=port,
        failure_message="Failed to ensure that consul was configured"
    )
    return exit_code


def ensure_consul_installed(host, port=22):
    """
    Install consul. This is done with scripting instead of puppet for ansible because at this point in the code
    no guarantees can be made about the remote host's environment.
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Ensuring consul is installed")
    ensure_consul_dependencies(host, port=port)
    ensure_latest_consul_release(host, port=port)
    unzip_consul_release(host, port=port)
    consul_setup(host, port=port)
