from argparse import ArgumentParser

from raptiformica.actions.slave import slave_machine
from raptiformica.actions.spawn import spawn_machine
from raptiformica.settings.types import get_server_types, get_first_server_type, get_first_compute_type, \
    get_compute_types
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
    Parse the commandline options for provisioning and assimilating a machine
    into the network
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
    parser.add_argument('--server-type', type=str, default=get_first_server_type(),
                        choices=get_server_types(),
                        help='Specify a server type. Default is {}'.format(get_first_server_type()))
    return parse_arguments(parser)


def slave():
    """
    Provision and assimilate a machine into the network
    :return None:
    """
    args = parse_slave_arguments()
    slave_machine(
        args.host,
        port=args.port,
        assimilate=not args.no_assimilate,
        server_type=args.server_type
    )


def parse_spawn_arguments():
    """
    Parse the commandline options for spawning a machine
    :return dict args: parsed arguments
    """
    parser = ArgumentParser(
        description='Spawn a machine to slave and assimilate into the network'
    )
    parser.add_argument('--no-assimilate', action='store_true', default=False,
                        help='Only provision. Do not join or set up the distributed network.')
    parser.add_argument('--server-type', type=str, default=get_first_server_type(),
                        choices=get_server_types(),
                        help='Specify a server type. Default is {}'.format(get_first_server_type()))
    parser.add_argument('--compute-type', type=str, default=get_first_compute_type(),
                        choices=get_compute_types(),
                        help='Specify a compute type. Default is {}'.format(get_first_compute_type()))
    return parse_arguments(parser)


def spawn():
    """
    Spawn a machine to package or to slave into the network
    :return None:
    """
    args = parse_spawn_arguments()
    spawn_machine(
        assimilate=not args.no_assimilate,
        server_type=args.server_type,
        compute_type=args.compute_type,
    )
