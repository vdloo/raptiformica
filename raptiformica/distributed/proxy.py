from contextlib import contextmanager

from raptiformica.distributed.discovery import host_and_port_pairs_from_config
from raptiformica.distributed.exec import try_machine_command

from raptiformica.shell.ssh import forward_remote_port


@contextmanager
def forward_any_port(source_port, destination_port=None, predicate=None):
    """
    Forward a remote SSH port from the first machine in the cluster that evaluates
    the provided predicate as nonzero.
    :param int source_port: The remote port to forward
    :param int destination_port: The destination port on the local host to forward to.
    Defaults to source_port.
    :param list[str, ..] predicate: command as list which must exit nonzero for the host to be eligible
    to be used as the forward host.
    :return None:
    """
    predicate = predicate or ['/bin/true']
    host_and_port_pairs = host_and_port_pairs_from_config(cached=True)
    _, host, ssh_port = try_machine_command(
        host_and_port_pairs, predicate, attempt_limit=1
    )
    if not host:
        raise RuntimeError("Could not find a suitable host")
    with forward_remote_port(host, source_port, ssh_port=ssh_port,
                             destination_port=destination_port):
        yield
