from logging import getLogger
from os.path import expanduser, join

from shutil import rmtree

from raptiformica.actions.mesh import ensure_no_consul_running, stop_detached_cjdroute

log = getLogger(__name__)

LOCAL_STATE_DIRS = (
    '/usr/bin/cjdroute',
    '/usr/etc/cjdns',
    '/usr/bin/consul',
    '/opt/consul',
    '/usr/etc/raptiformica',
    '/usr/etc/raptiformica_default_provisioner',
    join(expanduser("~"), '.raptiformica.d'),
    '/root/.raptiformica.d'
)


def clean_local_state():
    """
    Remove all state so it is as if the local machine
    will join the cluster for the first time the next
    time it is slaved.

    Note that this should in theory never be necessary
    but it can be helpful for debugging to rule out any
    leaking state issues. For example it could be that
    one of the instances in the cluster tries to keep
    connecting to some stale node that for some reason
    isn't being removed from the settings causing the
    stability of the mesh to degrade.
    :return None:
    """
    log.info("Cleaning local state")
    ensure_no_consul_running()
    stop_detached_cjdroute()
    for path_to_clean in LOCAL_STATE_DIRS:
        log.debug("Removing {} if it exists".format(path_to_clean))
        rmtree(path_to_clean, ignore_errors=True)
