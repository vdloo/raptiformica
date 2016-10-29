from logging import getLogger
from time import sleep

from raptiformica.actions.prune import prune_local_machines
from raptiformica.distributed.discovery import host_and_port_pairs_from_config
from raptiformica.distributed.power import try_issue_shutdown
from raptiformica.settings.load import purge_config

log = getLogger(__name__)

SHUTDOWN_SLEEP = 10


def shutdown_all_instances():
    """
    Issue a shutdown on all instances
    # todo: Do this by sending an event instead of using consul exec
    :return None:
    """
    log.info("Sending shutdown to all connected")
    host_and_port_pairs = host_and_port_pairs_from_config()
    if try_issue_shutdown(host_and_port_pairs):
        # In case sending the shutdown was successful
        sleep(SHUTDOWN_SLEEP)  # Give the machines some time to shut down


def destroy_cluster(purge_artifacts=False, purge_modules=False):
    """
    Destroy the cluster and remove the cached config
    Note: For now only cleans up locally bound instances
    :param bool purge_artifacts: Remove all stored artifacts
    :param bool purge_modules: Remove all installed modules
    :return None:
    """
    shutdown_all_instances()
    log.info("Destroying all locally bound instances")
    prune_local_machines(force=True)
    purge_config(purge_artifacts=purge_artifacts, purge_modules=purge_modules)
