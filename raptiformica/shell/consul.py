from collections import defaultdict
from contextlib import suppress
from logging import getLogger
from os import remove

from os.path import isfile

from raptiformica.settings import conf
from raptiformica.shell.execute import run_multiple_labeled_commands
from raptiformica.shell.unzip import unzip
from raptiformica.shell.wget import wget

log = getLogger(__name__)

CONSUL_ARCHES = defaultdict(
    lambda: 'https://releases.hashicorp.com/consul/1.0.2/consul_1.0.2_linux_amd64.zip',
    i686='https://releases.hashicorp.com/consul/1.0.2/consul_1.0.2_linux_386.zip',
    x86_64='https://releases.hashicorp.com/consul/1.0.2/consul_1.0.2_linux_amd64.zip',
    armv7l='https://releases.hashicorp.com/consul/1.0.2/consul_1.0.2_linux_arm.zip'
)
CONSUL_RELEASE = CONSUL_ARCHES[conf().MACHINE_ARCH]
CONSUL_KV_REPOSITORY = 'https://github.com/vdloo/consul-kv'


def ensure_consul_dependencies(host=None, port=22):
    """
    Install consul dependencies. Each command in the loop should check for identifiers of a
    certain distro and then run the idempotent install command if that distro is detected.
    :param str host: hostname or ip of the remote machine, or None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Ensuring the consul dependencies are installed")

    ensure_consul_dependencies_commands = (
        ('archlinux', 'type pacman 1> /dev/null && '
                      'pacman -S --noconfirm wget unzip screen --needed || /bin/true'),
        ('debian', 'type apt-get 1> /dev/null && '
                   'apt-get install -yy wget unzip screen '
                   '|| /bin/true')
    )
    run_multiple_labeled_commands(
        ensure_consul_dependencies_commands, host=host, port=port,
        failure_message="Failed to run (if {}) install consul "
                        "dependencies command"
    )


def ensure_latest_consul_release(host=None, port=22):
    """
    Make sure the latest consul release is downloaded on the remote machine
    :param str host: hostname or ip of the remote machine, or None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Ensuring consul release {} is on disk "
             "on the remote machine".format(CONSUL_RELEASE.split('/')[-1]))
    with suppress(FileNotFoundError):
        # remove any previously existing zip in case we tried
        # before but the zip was corrupted
        remove(CONSUL_RELEASE.split('/')[-1])
    wget(
        CONSUL_RELEASE, host=host, port=port,
        failure_message="Failed to retrieve {}".format(
            CONSUL_RELEASE.split('/')[-1]
        )
    )


def unzip_consul_binary(host=None, port=22):
    """
    Unzip the consul binary to /usr/bin
    :param str host: hostname or ip of the remote machine, or None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Making sure the consul binary is placed in /usr/bin")
    unzip(
        CONSUL_RELEASE.split('/')[-1], '/usr/bin',
        host=host, port=port,
        failure_message="Failed to unpack the consul binary"
    )


def unzip_consul_release(host=None, port=22):
    """
    Unzip the consul binary to /usr/bin to the INSTALL_DIR
    :param str host: hostname or ip of the remote machine, or None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    unzip_consul_binary(host=host, port=port)


def ensure_consul_installed(host=None, port=22):
    """
    Install consul. This is done with scripting instead of puppet for ansible because at this point in the code
    no guarantees can be made about the remote host's environment.
    :param str host: hostname or ip of the remote machine, or None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :return None:
    """
    log.info("Ensuring consul is installed")
    if not isfile('/usr/bin/consul'):
        ensure_consul_dependencies(host=host, port=port)
        ensure_latest_consul_release(host=host, port=port)
        unzip_consul_release(host=host, port=port)
