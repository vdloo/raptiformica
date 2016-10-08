#!/usr/bin/env python3
from raptiformica.shell.consul import ensure_consul_installed
from raptiformica.shell.cjdns import ensure_cjdns_installed
from raptiformica.shell.execute import run_command


def main():
    """
    This function is the entry point for running the provisioning
    scripts for the tools required by raptiformica itself.
    :return None:
    """
    # todo: refactor this so that the shell commands below run on the local
    # host directly, instead of SSHing to the localhost and running it there
    run_command(
        "cat /dev/zero | ssh-keygen -f loopback -q -N '' > /dev/null 2>&1; "
        "eval $(ssh-agent -s); ssh-add loopback; "
        "cat loopback.pub >> ~/.ssh/authorized_keys",
        shell=True,
        buffered=False,
    )
    ensure_cjdns_installed('localhost')
    ensure_consul_installed('localhost')

if __name__ == '__main__':
    main()
else:
    raise RuntimeError(
        "This script is an entry point and can not be imported"
    )
