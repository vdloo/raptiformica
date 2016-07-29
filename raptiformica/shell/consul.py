from logging import getLogger

from raptiformica.shell.execute import raise_failure_factory
from raptiformica.shell.execute import run_command_remotely_print_ready

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
        ('archlinux', '"type -p pacman 1> /dev/null && '
                      'pacman -S --noconfirm wget unzip --needed || /bin/true"'),
        ('debian', '"type -p apt-get 1> /dev/null && '
                   '(apt-get update -yy && '
                   'apt-get install -yy wget unzip) || /bin/true"')
    )
    for d, command_as_string in ensure_consul_dependencies_commands:
        run_command_remotely_print_ready(
            ["sh", "-c", command_as_string],
            host, port=port,
            failure_callback=raise_failure_factory(
                "Failed to run (if {}) install consul "
                "dependencies command".format(d)
            ),
            buffered=False
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
    run_command_remotely_print_ready(
        ['wget', '-nc', CONSUL_RELEASE],
        host, port=port,
        failure_callback=raise_failure_factory(
            "Failed to retrieve latest consul release"
        ),
        buffered=False
    )


def unzip_consul_release(host, port=22):
    """
    Unzip the consul binary to /usr/bin
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Making sure the consul binary is placed in /usr/bin")
    run_command_remotely_print_ready(
        ['unzip', '-o', CONSUL_RELEASE.split('/')[-1],
         '-d', '/usr/bin'],
        host, port=port,
        failure_callback=raise_failure_factory(
            "Failed to unzip latest consul release"
        ),
        buffered=False
    )


def ensure_consul_installed(host, port=22):
    """
    Install consul. This is done with scripting instead of puppet for ansible because at this point in the code
    no guarantees can be made about the remote host's environment.
    :param str host: hostname or ip of the remote machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Ensuring consul is installed")
    ensure_latest_consul_release(host, port=port)
    ensure_consul_dependencies(host, port=port)
    unzip_consul_release(host, port=port)
