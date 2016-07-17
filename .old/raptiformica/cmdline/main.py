from argparse import ArgumentParser
from glob import glob
from json import loads as load_json
from random import choice

from raptiformica.actions.machine.list import list_all, list_remote, list_local, set_of_all_machines_on_all_backends
from raptiformica.actions.machine.show import show, show_all
from raptiformica.actions.machine.slave import slave_machine
from raptiformica.actions.machine.spawn import spawn_machine
from raptiformica.actions.machine.ssh import ssh
from raptiformica.backends.resolve import resolve_manage_machine
from raptiformica.log import setup_logging
from raptiformica.settings import PROJECT_DIR, INSTANCE_BACKEND_DEFAULT


def generate_backend_choices():
    glob_pattern = PROJECT_DIR + '/raptiformica/backends/*/manage_machine.py'
    backend_directories = glob(glob_pattern)
    return map(lambda backend_directory: backend_directory.split('/')[-2], backend_directories)


def parse_machine(multi_machine):
    try:
        return load_json(multi_machine)
    except ValueError:
        try:
            return resolve_manage_machine('vagrant').get_machine_config_from_machine_uuid(multi_machine)
        except:
            return resolve_manage_machine('docker').get_machine_config_from_machine_uuid(multi_machine)


def compose_main_parser():
    parser = ArgumentParser(description='Dynamic infrastructure creation')
    get_machine = parser.add_mutually_exclusive_group()
    get_machine.add_argument('--spawn', action='store_true', help="Create a new machine")
    parser.add_argument('--backend', help="What to use to create the machine (default {})"
                        .format(INSTANCE_BACKEND_DEFAULT),
                        choices=generate_backend_choices())
    get_machine.add_argument('--machine', help="Supply a machine (machine config json string or machine uuid)")
    get_machine.add_argument('--any', help="Use any random available machine", action='store_true')
    parser.add_argument('--slave', action='store_true', help="Welcome a new machine to the network. "
                                                             "Use --spawn or provide a machine path.")
    show_option = parser.add_mutually_exclusive_group()
    show_option.add_argument('--show', action='store_true', help='Display machine config')
    show_option.add_argument('--show_all', action='store_true', help='Display all configs')

    list_machines = parser.add_mutually_exclusive_group()
    list_machines.add_argument('--list', action='store_true', help='List all machines')
    list_machines.add_argument('--list_local', action='store_true', help='List all local machines')
    list_machines.add_argument('--list_remote', action='store_true', help='List all remote machines')
    parser.add_argument('--shell', action='store_true', help='SSH into the provided machine')

    parser.add_argument('--verbose', '-v', action='store_true')
    return parser


def validate_argument_combinations(args, parser):
    if any((args.slave, args.show, args.shell)) and not(any((args.machine, args.spawn, args.any))):
        parser.error("This action requires a machine. Either provide one or spawn a new one.")

    if args.backend and not args.spawn:
        parser.error("Can only provide backend when --spawn is used.")

    actions = (args.spawn, args.slave, args.show, args.show_all,
               args.list, args.list_local, args.list_remote,
               args.shell)
    if not(any(actions)):
        parser.error("Provide at least one action")


def resolve_multi_arguments(args, parser):
    if args.any:
        all_machines = list(set_of_all_machines_on_all_backends())
        if len(all_machines):
            args.machine = choice(all_machines)
        else:
            parser.error("No available machines.")
    if args.machine:
        args.machine = parse_machine(args.machine)
    return args


def parse_main():
    """
    Parse the commandline options for the main program and return the args
    :return dict args: parsed arguments
    """
    parser = compose_main_parser()
    args = parser.parse_args()
    setup_logging(debug=args.verbose)
    validate_argument_combinations(args, parser)
    return resolve_multi_arguments(args, parser)


def run_spawn(args):
    backend = args.backend or INSTANCE_BACKEND_DEFAULT
    args.machine = spawn_machine(backend) if args.spawn else args.machine
    return args


def run_slave(args):
    if args.slave:
        slave_machine(args.machine)


def run_show(args):
    if args.show:
        show(args.machine)
    if args.show_all:
        show_all()


def run_list(args):
    if args.list:
        list_all()
    if args.list_local:
        list_local()
    if args.list_remote:
        list_remote()


def run_shell(args):
    if args.shell:
        ssh(args.machine)


def process_main(args):
    args = run_spawn(args)
    run_slave(args)
    run_show(args)
    run_list(args)
    run_shell(args)


def run_main():
    args = parse_main()
    process_main(args)
