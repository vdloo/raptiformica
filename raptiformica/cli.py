from argparse import ArgumentParser

from raptiformica.actions.slave import slave_machine


def parse_slave_arguments():
    """
    Parse the commandline options for provisioning and joining a machine into the network
    :return dict args: parsed arguments
    """
    parser = ArgumentParser(
        description='Provision and join a machine into the network'
    )
    parser.add_argument('host', type='str',
                        help='Hostname or ip of the machine')
    parser.add_argument('--no-assimilate', action='store_true', default=False,
                        help='Only provision. Do not join or set up the distributed network.')
    return parser.parse_args()


def slave():
    """
    Provision and join a machine into the network
    :return None:
    """
    args = parse_slave_arguments()
    slave_machine(args.host, assimilate=not args.no_assimilate)
