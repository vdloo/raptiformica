#!/usr/bin/env python3
from raptiformica.log import setup_logging
from raptiformica.shell.consul import ensure_consul_installed
from raptiformica.shell.cjdns import ensure_cjdns_installed


def main():
    """
    This function is the entry point for running the provisioning
    scripts for the tools required by raptiformica itself.
    :return None:
    """
    setup_logging()
    # todo: refactor this so that the shell commands below run on the local
    # host directly, instead of SSHing to the localhost and running it there
    ensure_cjdns_installed('localhost')
    ensure_consul_installed('localhost')

if __name__ == '__main__':
    main()
else:
    raise RuntimeError(
        "This script is an entry point and can not be imported"
    )
