from argparse import ArgumentParser

from raptiformica.actions.hook import trigger_handlers
from raptiformica.actions.members import rejoin_members, show_members
from raptiformica.actions.mesh import mesh_machine
from raptiformica.actions.modules import load_module, unload_module
from raptiformica.actions.prune import prune_local_machines
from raptiformica.actions.slave import slave_machine
from raptiformica.actions.destroy import destroy_cluster
from raptiformica.actions.spawn import spawn_machine
from raptiformica.actions.ssh_connect import ssh_connect
from raptiformica.actions.update import update_machine
from raptiformica.settings import MUTABLE_CONFIG
from raptiformica.settings.types import get_server_types, get_first_server_type, get_first_compute_type, \
    get_compute_types
from raptiformica.log import setup_logging


def parse_arguments(parser):
    """
    Add default parser arguments to parser and parse arguments. Also sets logging level.
    :param obj parser:
    :return obj args: parsed arguments
    """
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()
    setup_logging(debug=args.verbose)
    return args


def parse_slave_arguments():
    """
    Parse the commandline options for provisioning and assimilating a machine
    into the network
    :return obj args: parsed arguments
    """
    parser = ArgumentParser(
        prog="raptiformica slave",
        description='Provision and join a machine into the network'
    )
    parser.add_argument('host', type=str,
                        help='Hostname or ip of the machine')
    parser.add_argument('--port', '-p', type=int, default=22,
                        help='Port to use to connect to the remote machine with over SSH')
    parser.add_argument('--no-provision', action='store_true', default=False,
                        help='Do not run the provisioning scripts for the specified server type')
    parser.add_argument('--no-assimilate', action='store_true', default=False,
                        help='Do not join or set up the distributed network.')
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
        provision=not args.no_provision,
        server_type=args.server_type
    )


def parse_update_arguments():
    """
    Parse the commandline options for updating existing machines
    :return obj args: parsed arguments
    """
    parser = ArgumentParser(
        prog="raptiformica update",
        description='Update the local machine by running the configured '
                    'commands from the installed provisioning modules'
    )
    parser.add_argument(
        '--server-type', type=str, default=get_first_server_type(),
        choices=get_server_types(),
        help='Specify a server type. Default is {}'.format(
            get_first_server_type()
        )
    )
    return parse_arguments(parser)


def update():
    """
    Update an existing machine
    :return None:
    """
    args = parse_update_arguments()
    update_machine(server_type=args.server_type)


def parse_spawn_arguments():
    """
    Parse the commandline options for spawning a machine
    :return obj args: parsed arguments
    """
    parser = ArgumentParser(
        prog="raptiformica spawn",
        description='Spawn a machine to slave and assimilate into the network'
    )
    parser.add_argument('--no-provision', action='store_true', default=False,
                        help='Do not run the provisioning scripts for the specified server type')
    parser.add_argument('--no-assimilate', action='store_true', default=False,
                        help='Do not join or set up the distributed network.')
    parser.add_argument('--server-type', type=str, default=get_first_server_type(),
                        choices=get_server_types(),
                        help='Specify a server type. Default is {}'.format(get_first_server_type()))
    parser.add_argument('--compute-type', type=str, default=get_first_compute_type(),
                        choices=get_compute_types(),
                        help='Specify a compute type. Default is {}'.format(get_first_compute_type()))
    parser.add_argument('--check-available', action='store_true',
                        help="Check if there is a configured server and compute type available on this host")
    return parse_arguments(parser)


def spawn():
    """
    Spawn a machine to package or to slave into the network
    :return None:
    """
    args = parse_spawn_arguments()
    spawn_machine(
        assimilate=not args.no_assimilate,
        provision=not args.no_provision,
        server_type=args.server_type,
        compute_type=args.compute_type,
        check_available=args.check_available
    )


def parse_mesh_arguments():
    """
    Parse the commandline options for joining a machine
    into the distributed network
    :return obj args: parsed arguments
    """
    parser = ArgumentParser(
        prog="raptiformica mesh",
        description='Deploy a mesh configuration based on the {} config '
                    'file on this machine and attempt to join '
                    'the distributed network'.format(MUTABLE_CONFIG)
    )
    return parse_arguments(parser)


def mesh():
    """
    Join this machine into the distributed network
    :return None:
    """
    parse_mesh_arguments()
    mesh_machine()


def parse_hook_arguments():
    """
    Parse the commandline options for running a hook
    :return obj args: parsed arguments
    """
    parser = ArgumentParser(
        prog="raptiformica hook",
        description='Run all handlers for a specific hook from the config'
    )
    parser.add_argument(
        'name', type=str,
        help='Name of the hook to fire. i.e. after_mesh or cluster_change'
    )
    return parse_arguments(parser)


def hook():
    """
    Run the handlers for a specific hook
    :return None:
    """
    args = parse_hook_arguments()
    # todo: In the future this could pass the input from stdin down to
    # each handler so that the json provided on stdin by consul watches
    # that trigger this hook can be used to perform actions based on the
    # content of the event.
    trigger_handlers(hook_name=args.name)


def parse_ssh_arguments():
    """
    Parse the commandline options for connecting to one of the machines over SSH
    :return obj args: parsed arguments
    """
    parser = ArgumentParser(
        prog="raptiformica ssh",
        description="SSH into one of the machines"
    )
    parser.add_argument(
        '--info-only', '--only-info', action='store_true',
        help="Don't get a shell. Only print the command to connect."
    )
    return parse_arguments(parser)


def ssh():
    """
    Connect to one of the machines over ssh
    :return None:
    """
    args = parse_ssh_arguments()
    ssh_connect(info_only=args.info_only)


def parse_members_arguments():
    """
    Parse the commandline options for managing the members in the distributed network
    :return obj args: parsed arguments
    """
    parser = ArgumentParser(
        prog="raptiformica members",
        description="Manage the members of the distributed network."
    )
    parser.add_argument(
        '--rejoin', '-r', action='store_true',
        help='Attempt to (re)join all members found in the available config'
    )
    return parse_arguments(parser)


def members():
    """
    Manage the members of the distributed network
    :return None:
    """
    args = parse_members_arguments()
    if args.rejoin:
        rejoin_members()
    else:
        show_members()


def parse_prune_arguments():
    """
    Parse the commandline options for pruning stale machines. Will run the configured clean_up_stale_instance
    command for the server type at the compute type for each inactive machine and will clean up the instance checkout
    :return obj args: parsed arguments
    """
    parser = ArgumentParser(
        prog="raptiformica prune",
        description="Clean up inactive instances"
    )
    return parse_arguments(parser)


def prune():
    """
    Clean up inactive instances
    :return None:
    """
    parse_prune_arguments()
    prune_local_machines()


def parse_destroy_arguments():
    """
    Parse the commandline options for destroying the cluster. Will shutdown and prune all machines. Removes config.
    :return obj args: parsed arguments
    """
    parser = ArgumentParser(
        prog="raptiformica destroy",
        description="Clean up the cluster"
    )
    parser.add_argument(
        '--purge-artifacts', action='store_true',
        help='Remove all stored artifacts'
    )
    parser.add_argument(
        '--purge-modules', action='store_true',
        help='Remove all loaded modules'
    )
    return parse_arguments(parser)


def destroy():
    """
    Clean up the cluster
    :return None:
    """
    args = parse_destroy_arguments()
    destroy_cluster(
        purge_artifacts=args.purge_artifacts, purge_modules=args.purge_modules
    )


def parse_modprobe_arguments():
    """
    Parse the commandline options for loading or unloading a module into the system.
    :return obj args: parsed arguments
    """
    parser = ArgumentParser(
        prog="raptiformica modprobe",
        description="Load or unload a module into the system"
    )
    parser.add_argument(
        'name', type=str,
        help='Name of the module to load or '
             'unload. Like "vdloo/puppetfiles"'
    )
    parser.add_argument(
        '--remove', '-r', action='store_true',
        help='Unload the module'
    )
    return parse_arguments(parser)


def modprobe():
    """
    Load or unload a module into the system
    :return None:
    """
    args = parse_modprobe_arguments()
    if args.remove:
        unload_module(args.name)
    else:
        load_module(args.name)
