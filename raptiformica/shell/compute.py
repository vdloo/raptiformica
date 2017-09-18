from logging import getLogger
from os import path
from uuid import uuid4

from raptiformica.settings import conf
from raptiformica.shell.execute import log_success_factory, raise_failure_factory, \
    run_command_print_ready_in_directory_factory
from raptiformica.shell.git import clone_source
from raptiformica.utils import ensure_directory

log = getLogger(__name__)

BOOT_INSTANCE_TIMEOUT = 1800


def ensure_new_compute_checkout_directory_exists(server_type, compute_type):
    """
    Ensure the ephemeral directory structure for a server type of a compute type
    :param str server_type: name of the server type
    :param str compute_type: name of the compute type
    :return str server_type_directory: directory for the server type of the compute type
    """
    compute_type_directory = path.join(conf().MACHINES_DIR, compute_type)
    server_type_directory = path.join(compute_type_directory, server_type)
    directories = conf().EPHEMERAL_DIR, conf().MACHINES_DIR, \
        compute_type_directory, server_type_directory
    for directory in directories:
        ensure_directory(directory)
    return server_type_directory


def create_new_compute_checkout(server_type, compute_type, source):
    """
    Create a new directory for an instance of a server type of a compute type
    :param str server_type: name of the server type
    :param str compute_type: name of the compute type
    :param str source: repository for the compute type
    :return str new_compute_directory: directory of the new checkout
    """
    server_type_directory = ensure_new_compute_checkout_directory_exists(
        server_type, compute_type
    )
    new_compute_checkout = path.join(server_type_directory, uuid4().hex)
    clone_source(source, new_compute_checkout)
    return new_compute_checkout


def boot_instance(new_compute_checkout, command):
    """
    Run the start instance command
    :param str new_compute_checkout: path to the new compute checkout
    :param str command: start instance command
    :return tuple connection_information: host and port
    """
    log.info("Booting new instance, this can take a while..")
    partial_run_command = run_command_print_ready_in_directory_factory(
        new_compute_checkout, command
    )
    exit_code, _, _ = partial_run_command(
        success_callback=log_success_factory("Booted a new instance"),
        failure_callback=raise_failure_factory(
            "Failed to start the compute type"
        ),
        timeout=BOOT_INSTANCE_TIMEOUT,
        buffered=False
    )
    return exit_code


def compute_attribute_get(new_compute_checkout, getter_command, attribute_description):
    """
    Get an attribute of the new compute checkout by running the getter_command in the new checkout directory
    :param str new_compute_checkout: path to the new compute checkout
    :param str getter_command: command that gets an attribute of the new compute instance
    Example: cd headless && vagrant ssh-config | grep HostName | awk '{print$NF}'
    :param attribute_description: how to refer to the attribute as in the logs. i.e. hostname
    :return str standard_out: the output from the getter_command
    """
    log.info("Getting the {} from the instance bound to {}".format(
        attribute_description, new_compute_checkout
    ))
    partial_run_command_print_ready = run_command_print_ready_in_directory_factory(
        new_compute_checkout, getter_command
    )
    _, standard_out, _ = partial_run_command_print_ready(
        failure_callback=raise_failure_factory(
            "Failed to get {} in {}!".format(
                attribute_description, new_compute_checkout
            )
        ),
    )
    return standard_out.strip()


def start_instance(server_type, compute_type, source, boot_command, get_hostname_command, get_port_command):
    """
    Start a compute instance
    :param str server_type: name of the server type
    :param str compute_type: name of the compute type
    :param str source: repository for the compute type
    :param str boot_command: start instance command
    :param str get_hostname_command: get hostname command
    :param str get_port_command: get port command
    :return tuple compute_checkout_information: compute_checkout_uuid, host and port
    """
    log.info("Starting a new {} instance".format(compute_type))
    new_compute_checkout = create_new_compute_checkout(
        server_type, compute_type, source
    )
    boot_instance(new_compute_checkout, boot_command)
    host = compute_attribute_get(
        new_compute_checkout, get_hostname_command, "hostname"
    )
    port = compute_attribute_get(
        new_compute_checkout, get_port_command, "port"
    )
    compute_checkout_uuid = new_compute_checkout.split('/')[-1]
    return compute_checkout_uuid, host, port
