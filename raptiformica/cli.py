from argparse import ArgumentParser

from raptiformica.actions.slave import slave_machine
from raptiformica.log import setup_logging


def parse_arguments(parser):
    """
    Add default parser arguments to parser and parse arguments. Also sets logging level.
    :param obj parser:
    :return dict args: parsed arguments
    """
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()
    setup_logging(debug=args.verbose)
    return args


def parse_slave_arguments():
    """
    Parse the commandline options for provisioning and joining a machine into the network
    :return dict args: parsed arguments
    """
    parser = ArgumentParser(
        description='Provision and join a machine into the network'
    )
    parser.add_argument('host', type=str,
                        help='Hostname or ip of the machine')
    parser.add_argument('--port', '-p', type=int, default=22,
                        help='Port to use to connect to the remote machine with over SSH')
    parser.add_argument('--no-assimilate', action='store_true', default=False,
                        help='Only provision. Do not join or set up the distributed network.')
    return parse_arguments(parser)


def slave():
    """
    Provision and join a machine into the network
    :return None:
    """
    args = parse_slave_arguments()
    slave_machine(args.host, port=args.port, assimilate=not args.no_assimilate)
